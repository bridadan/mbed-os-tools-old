import os

class MbedDevice(object):
    '''Class for representing an Mbed device'''

    # Public methods and properties
    def __init__(self, usb_device):
        '''Create an MbedDevice from a UsbDevice

        @param usb_device The UsbDevice instance that represents the MbedDevice
        '''
        self._usb_device = usb_device

    @property
    def usb_device(self):
        '''Return the UsbDevice associated with the MbedDevice'''
        return self._usb_device

    @property
    def mount_point(self):
        '''The cached mount point for the MbedDevice

        This value is cached, meaning it will only be updated when update() is called.
        '''
        return self._usb_device.mount_point

    @property
    def serial_port(self):
        '''The cached serial port for the MbedDevice

        This value is cached, meaning it will only be updated when update() is called.
        '''
        return self._usb_device.serial_port

    def update(self):
        '''Update the cached values for the Mbed Device

        This will use the UsbDevice to query the system for information about
        this device.
        '''
        self._usb_device.update()
