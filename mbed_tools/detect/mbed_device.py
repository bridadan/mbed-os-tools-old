import os

class MbedDevice(object):
    '''Class for describing a Mbed device'''

    # Public types
    class CachedPropertyException(Exception):
        pass

    # Public methods and properties
    def __init__(self, usb_device, update=True):
        self._usb_device = usb_device
        self._details = {}

        if update:
            self.update()

    @property
    def usb_device(self):
        return self._usb_device

    @property
    def mount_point(self):
        return self._get_cached_property('mount_point')

    @property
    def serial_port(self):
        return self._get_cached_property('serial_port')

    def update(self):
        self._details['mount_point'] = self._usb_device.mount_point()
        self._details['serial_port'] = self._usb_device.serial_port()

    # Private methods

    def _get_cached_property(self, property_name):
        if property_name in self._details:
            return self._details[property_name]
        else:
            raise self.CachedPropertyException(
                'Property "{}" is not cached'.format(property_name)
            )

