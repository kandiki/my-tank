from flask import (Blueprint, request)
from . import appliance

admin_controller = Blueprint('admin-controller', __name__, url_prefix='/api/admin')

@admin_controller.route('/server/update', methods=["GET", "POST"])
def api_admin_server_update():
    if request.method == "POST":
        gitStatus = appliance.updateSource()
        return {'gitPullStatus': gitStatus}
    elif request.method == "GET":
        gitStatus = appliance.checkUpdate()
        return {'gitStatus': gitStatus}

@admin_controller.route('/server/appliance', methods=["POST"])
def api_admin_appliance_restart():
    if request.method == "POST":
        status = appliance.restartAppliance()
        return {'applianceRestartStatus': status}




