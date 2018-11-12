import os

class MbedDevice(object):
    '''Class for representing an Mbed device'''

    # Public types
    class CachedPropertyException(Exception):
        '''Exception used to indicate a property is not in the cache'''
        pass

    # Public methods and properties
    def __init__(self, usb_device, update=True):
        '''Create an MbedDevice from a UsbDevice

        @param usb_device The UsbDevice instance that represents the MbedDevice
        @param update If True, the UsbDevice will be used to query the system
        for information about the device. Setting this to False may be useful when
        the timing of accessing the system is critical.
        '''
        self._usb_device = usb_device
        self._cache = {}

        if update:
            self.update()

    @property
    def usb_device(self):
        '''Return the UsbDevice associated with the MbedDevice'''
        return self._usb_device

    @property
    def mount_point(self):
        '''The cached mount point for the MbedDevice

        This value is cached, meaning it will only be updated when update() is called.
        If update() has not been called before this is accessed, it will raise a
        CachedPropertyException.
        '''
        return self._get_cached_property('mount_point')

    @property
    def serial_port(self):
        '''The cached serial port for the MbedDevice

        This value is cached, meaning it will only be updated when update() is called.
        If update() has not been called before this is accessed, it will raise a
        CachedPropertyException.
        '''
        return self._get_cached_property('serial_port')

    def update(self):
        '''Update the cached values for the Mbed Device

        This will use the UsbDevice to query the system for information about
        this device.
        '''
        self._cache['mount_point'] = self._usb_device.mount_point()
        self._cache['serial_port'] = self._usb_device.serial_port()

    # Private methods

    def _get_cached_property(self, property_name):
        if property_name in self._cache:
            return self._cache[property_name]
        else:
            raise self.CachedPropertyException(
                'Property "{}" is not cached'.format(property_name)
            )

