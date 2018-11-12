import os
from abc import ABCMeta, abstractmethod

class UsbDevice(object):
    '''Class for describing a USB device'''

    # We use the __metaclass__ syntax here because inheriting from the
    # ABC class is not supported in Python 2.7.x
    __metaclass__ = ABCMeta

    @abstractmethod
    def mount_point(self):
    '''Query the system for the mount point associated with the UsbDevice

    @return If mounted, a string of the mount point.
    Otherwise, None.
    '''
        raise NotImplementedError

    @abstractmethod
    def serial_port(self):
    '''Query the system for the serial port associated with the UsbDevice

    @return If a serial port exists, a string representing the serial port.
    Otherwise, None.
    '''
        raise NotImplementedError
