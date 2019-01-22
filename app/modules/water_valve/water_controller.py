from flask import (Blueprint, request)
import water

water_controller = Blueprint('water-controller', __name__, url_prefix='/api/water')

@water_controller.route('/', methods=["GET"])
def api_water_control():
    return {'flowStatus': water.value()}

@water_controller.route('/on', methods=["GET", "POST"])
def api_water_on():
    if request.method == "POST":
        water.on()

    return {'flowStatus': water.value()}

@water_controller.route('/off', methods=["GET", "POST"])
def api_water_off():
    if request.method == "POST":
        water.off()

    return {'flowStatus': water.value()}

@water_controller.route('/toggle', methods=["GET", "POST"])
def api_water_toggle():
    if request.method == "POST":
        water.toggle()

    return {'flowStatus': water.value()}