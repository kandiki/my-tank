#!/usr/bin/python
import logging
import json
import os.path
from os import path
from .plugs import TplinkPlug
from app.modules.devices import (
    Device,
    OnboardRelay,
)

_DATA_DIR = '/var/lib/weegrow-data/devices/'

def save_device(device: Device):
    f = open(_DATA_DIR + device.encoded_alias + '.json', 'w+')
    device.save(f)
    return

def delete_device(encoded_alias: str):
    full_path = _DATA_DIR + encoded_alias + '.json'
    if os.path.exists(full_path):
        os.remove(full_path)
    return

def retrieve_device(encoded_alias):
    device = None

    file_name = encoded_alias + '.json'
    device = _retrieve_device_from_file(file_name)

    return device

def retrieve_devices():
    devices = []
    for file_name in os.listdir(_DATA_DIR):
        device = None
        if file_name.endswith(".json"):
            device = _retrieve_device_from_file(file_name)

        #if lookup worked, add to devices 
        if device:
            devices.append(device)

    return devices
        
def _retrieve_device_from_file(file_name):
    device = None
    f = open(_DATA_DIR + file_name)
    json_data = f.read()
    if json_data:
        device_props = json.loads(json_data)
        device_class = device_props.get('class')
        if device_class == 'OnboardRelay':
            device = OnboardRelay(device_props['alias'], device_props['gpio'])
        else:
            device = TplinkPlug(device_props['alias'], device_props['host'])
            
    f.close()
    return device