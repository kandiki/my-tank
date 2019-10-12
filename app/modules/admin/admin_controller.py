from flask import (Blueprint, request, jsonify)
from . import appliance
from . import Network, WifiNetwork, Wifi
from app.modules.devices.unearth import Unearth
from app.modules.devices.plugs.tplinkplug import TplinkPlug
from app.modules.devices import manager
import os

admin_controller = Blueprint('admin-controller', __name__, url_prefix='/api/admin')

def wifi_network_response(wifi_network):
    return {
        'bssid': wifi_network.bssid,
        'ssid': wifi_network.ssid,
        'channel': wifi_network.channel,
        'frequency': wifi_network.frequency,
        'mode': wifi_network.mode,
        'type': wifi_network.type,
        'privacy': wifi_network.privacy,
        'signal_dbm': wifi_network.signal_dbm,
        'signal_quality': wifi_network.signal_quality
    }

def network_response(network):
    if network:
        return {
            'enabled': network.enabled,
            'ssid':  network.ssid,
            'priority': network.priority,
            'path': network.path
        }
    else:
        return {
            'enabled': '',
            'ssid':  '',
            'priority': '',
            'path': ''
        }
    return {
        'enabled': network.enabled,
        'ssid':  network.ssid,
        'priority': network.priority,
        'path': network.path
    }

def device_response(device):
    if device:
        return {
            'name': device.alias,
            'host': device.host,
            'brand': device.brand,
            'style':device.style,
            'sys_info': device.sys_info
        }
    else:
        return {
            'name': '',
            'host': '',
            'brand': '',
            'style': '',
            'sys_info': ''
        }
    

@admin_controller.route('/server', methods=["GET", "POST"])
def api_admin_server_status():
    if request.method == "POST":
        appliance.appliance_restart()
        return {'applianceRestartStatus': 'Restarting....'}
    elif request.method == "GET":
        appliance_state = appliance.appliance_state()
        app_state = appliance.app_state()
        prometheus_state = appliance.prometheus_state()
        app_updatable = appliance.app_update_available()
        appliance_updatable = appliance.appliance_update_available()
        return {'weegrowApplianceStatus': appliance_state, 
            'weegrowAppStatus': app_state, 
            'weegrowStatsDbStatus':prometheus_state,
            'weegrowAppUpdateAvailable':app_updatable,
            'weegrowApplianceUpdateAvailable':appliance_updatable
            }

@admin_controller.route('/server/appliance', methods=["GET", "POST"])
def api_admin_appliance():
    if request.method == "POST":
        appliance.appliance_restart()
        return {'applianceRestartStatus': 'Restarting....'}
    elif request.method == "GET":
        state = appliance.appliance_state()
        return {'applianceStatus': state }

@admin_controller.route('/server/appliance/update', methods=["GET", "POST"])
def api_admin_server_update():
    if request.method == "POST":
        gitStatus = appliance.update_source()
        return {'gitPullStatus': gitStatus}
    elif request.method == "GET":
        gitStatus = appliance.check_update()
        update_available = appliance.appliance_update_available()
        return {'updateAvailable' : update_available, 'gitStatus': gitStatus}

@admin_controller.route('/server/weegrow-app', methods=["GET", "POST"])
def api_admin_app():
    if request.method == "POST":
        status = appliance.app_restart()
        return {'weegrowAppStatus': status}
    elif request.method == "GET":
        app_state = appliance.app_state()
        return {'weegrowAppStatus': app_state }

@admin_controller.route('/server/weegrow-app/update', methods=["GET", "POST"])
def api_admin_app_update():
    if request.method == "POST":
        update_status = appliance.app_update()
        return {'weegrowAppUpdateStatus': update_status}
    elif request.method == "GET":
        update_status = appliance.app_update_available()
        return {'weegrowAppUpdateAvailable': update_status }

@admin_controller.route('/server/update-restart', methods=["GET", "POST"])
def api_update_restart():
    if request.method == "POST":
        update_status = appliance.app_update()
        app_status = appliance.app_restart()
        gitStatus = appliance.update_source()
        appliance.update_dependencies()
        appliance.appliance_restart()
        return {'weegrowAppUpdateAvailable': update_status, 
            'weegrowApplianceUpdateAvailable': gitStatus,
            'weegrowAppStatus': app_status,
            'weegroqApplianceStatus': 'restarting'}
    elif request.method == "GET":
        update_status = appliance.app_update_available()
        gitStatus = appliance.appliance_update_available()
        app_status = appliance.app_state()
        appliance_status = appliance.appliance_state()
        return {'weegrowAppUpdateAvailable': update_status,
            'weegrowApplianceUpdateAvailable': gitStatus,
            'weegrowAppStatus': app_status,
            'weegrowApplianceStatus': appliance_status}

@admin_controller.route('/server/wifi/scan', methods=["GET"])
def api_wifi_ssids():
    if request.method == "GET":
        
        networks = Wifi().scan()

        response_list = []
        for wifi_network in networks:
            response_list.append(wifi_network_response(wifi_network))

        return {'wifiNetworksAvailable': response_list}

@admin_controller.route('/server/wifi/networks', methods=["GET", "POST"])
def api_wifi_networks():
    wifi = Wifi()
    if request.method == "POST":
        wifi.save_config()

    saved_networks = wifi.get_known_networks()

    response_list = []
    for saved_network in saved_networks:
        response_list.append(network_response(saved_network))

    return {'savedNetworks': response_list}

@admin_controller.route('/server/wifi/networks/<name>', methods=["GET", "POST", "DELETE"])
def api_wifi_network(name):
    wifi = Wifi()
    if request.method == "GET":
        return {'network': network_response(wifi.get_network_info(name))}
    elif request.method == "POST":
        psk = request.data.get('psk')
        enabled = request.data.get('enabled', 'True') == 'True'
        priority = request.data.get('priority', '0')
        saved_network = wifi.save_network(name, psk, enabled, priority)

        return {'network': network_response(saved_network)}
    elif request.method == "DELETE":
        wifi.delete_network(name)
        return {'network': network_response(wifi.get_network_info(name))}

@admin_controller.route('/server/wifi/networks/active', methods=["GET"])
def api_active_networks():
    if request.method == "GET":
        active_network = Wifi().get_active_network()

        return {'networks': network_response(active_network)}

@admin_controller.route('/server/wifi/networks/<name>/activate', methods=["GET", "POST"])
def api_activate_network(name):
    wifi = Wifi()
    if request.method == "GET":
        active_name = wifi.get_active_network().ssid
        if name.lower() == active_name.lower():
            return{'isActive': "True"}
        else:
            return {'isActive': "False"}
    elif request.method == "POST":
        wifi.activate_network(name)

        return{'isActive': "True"}

@admin_controller.route('/server/wifi/networks/ap-mode', methods=["GET", "POST", "DELETE"])
def api_network_ap_mode():
    wifi = Wifi()
    if request.method == "POST":
        wifi.enable_ap_mode()
    elif request.method == "DELETE":
        wifi.disable_ap_mode()

    if wifi.is_ap_mode:
        return{'isApMode': "True"}
    else:
        return {'isApMode': "False"}
