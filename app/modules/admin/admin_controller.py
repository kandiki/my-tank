from flask import (Blueprint, request)
from . import appliance
import os

admin_controller = Blueprint('admin-controller', __name__, url_prefix='/api/admin')

@admin_controller.route('/server/update', methods=["GET", "POST"])
def api_admin_server_update():
    if request.method == "POST":
        gitStatus = appliance.update_source()
        return {'gitPullStatus': gitStatus}
    elif request.method == "GET":
        gitStatus = appliance.check_update()
        return {'gitStatus': gitStatus}

@admin_controller.route('/server', methods=["GET", "POST"])
def api_admin_server_status():
    if request.method == "POST":
        applianceStatus = appliance.appliance_restart()
        return {'appliance_restartStatus': applianceStatus}
    elif request.method == "GET":
        appliance_state = appliance.appliance_state()
        app_state = appliance.app_state()
        prometheus_state = appliance.prometheus_state()
        return {'weegrow-appliance': appliance_state, 'weegrow_app': app_state, "weegrow_stats_db":prometheus_state}

@admin_controller.route('/server/appliance', methods=["GET", "POST"])
def api_admin_appliance():
    if request.method == "POST":
        status = appliance.appliance_restart()
        return {'appliance_restartStatus': status}
    elif request.method == "GET":
        state = appliance.appliance_state()
        return {'appliance_state': state }

@admin_controller.route('/server/weegrow-app', methods=["GET", "POST"])
def api_admin_app():
    if request.method == "POST":
        app_status = appliance.app_update()
        return {'weegrow_app': app_status}
    elif request.method == "GET":
        app_state = appliance.app_state()
        return {'weegrow_app': app_state }


