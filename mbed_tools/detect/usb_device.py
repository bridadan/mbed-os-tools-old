import os
from abc import ABCMeta, abstractmethod

class UsbDevice(object):
    '''Class for describing a USB device'''

    # We use the __metaclass__ syntax here because inheriting from the
    # ABC class is not supported in Python 2.7.x
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self):
        '''Query the system and update the UsbDevice's information'''
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self):
        '''Return a string representing the USB id'''
        raise NotImplementedError

    @property
    @abstractmethod
    def vendor_id(self):
        '''Return a string representing the USB vendor id

        The format of the vendor id should be a lowercase, hexidecimal, 4 character string
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def product_id(self):
        '''Return a string representing the USB product id

        The format of the vendor id should be a lowercase, hexidecimal, 4 character string
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def mount_point(self):
        '''Return a string representing the mount point. If not mounted, return None

        This value is cached, meaning it will only be updated when update() is called.
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def serial_port(self):
        '''Return a string representing the serial port. If none exists, return None

        This value is cached, meaning it will only be updated when update() is called.
        '''
        raise NotImplementedError
