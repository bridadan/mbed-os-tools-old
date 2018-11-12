import os
from abc import ABCMeta, abstractmethod

class UsbDevice(object):
    '''Class for describing a USB device'''

    # We use the __metaclass__ syntax here because inheriting from the
    # ABC class is not supported in Python 2.7.x
    __metaclass__ = ABCMeta

    @abstractmethod
    def mount_point(self):
        raise NotImplementedError

    @abstractmethod
    def serial_port(self):
        raise NotImplementedError
