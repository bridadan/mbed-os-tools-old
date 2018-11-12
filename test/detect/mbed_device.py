#!/usr/bin/env python
# coding: utf-8
"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
import sys
import os
from mock import MagicMock, patch, call

from mbed_tools.detect import MbedDevice

_USB_DEVICE_PROPERTIES = ('mount_point', 'serial_port')
_USB_DEVICE_ATTRS = {
    '{}.return_value'.format(p): p for p in _USB_DEVICE_PROPERTIES
}


class MbedDeviceTestCase(unittest.TestCase):
    '''Tests for the MbedDevice class'''

    def test_construct_default_update_true(self):
        '''
        Ensure the constructor accesses the UsbDevice information when either
        no argumentsare are supplied or when the update=True argument is supplied
        '''

        def test_helper(**kwargs):
            usb_device = MagicMock(**_USB_DEVICE_ATTRS)
            mbed_device = MbedDevice(usb_device, **kwargs)

            for property_name in _USB_DEVICE_PROPERTIES:
                getattr(usb_device, property_name).assert_called()
                self.assertEqual(getattr(mbed_device, property_name), property_name)

        test_helper()
        test_helper(update=True)

    def test_construct_with_update_false(self):
        '''
        Ensure the constructor does not access the UsbDevice information when
        the update=False argument is supplied
        '''

        usb_device = MagicMock(**_USB_DEVICE_ATTRS)
        mbed_device = MbedDevice(usb_device, update=False)

        for property_name in _USB_DEVICE_PROPERTIES:
            getattr(usb_device, property_name).assert_not_called()
            self.assertRaises(MbedDevice.CachedPropertyException, getattr, mbed_device, property_name)

    def test_update(self):
        '''
        Calling update() on an MbedDevice should access all UsbDevice properties
        '''

        usb_device = MagicMock(**_USB_DEVICE_ATTRS)
        # Call with update=False to prevent MbedDevice from accessing the UsbDevice
        mbed_device = MbedDevice(usb_device, update=False)
        mbed_device.update()

        for property_name in _USB_DEVICE_PROPERTIES:
            getattr(usb_device, property_name).assert_called()
            self.assertEqual(getattr(mbed_device, property_name), property_name)
