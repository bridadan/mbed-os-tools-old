import sys
import importlib

# Bring APIs and classes into the 'detect' module
from .mbed_device import MbedDevice
from .usb_device import UsbDevice

_OS_MODULE_NAMES = {
    'win32': 'windows',
    'linux': 'linux',
    'darwin': 'darwin'
}

def find_usb_devices():
    '''Call the OS-specific version of find_usb_devices()

    Raises an Exception if the OS is not supported.
    '''
    module_name = None
    for os_name, os_module_name in _OS_MODULE_NAMES.items():
        if sys.platform.startswith(os_name):
            module_name = os_module_name

    if not module_name:
        raise Exception(
            'Detecting devices on platform "{}" is unsupported'.format(sys.platform)
        )

    module = importlib.import_module('.' + module_name, 'mbed_tools.detect')
    return module.find_usb_devices()
