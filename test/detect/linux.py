#!/usr/bin/env python
'''
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import unittest
import sys
import os
from mock import patch, mock_open
import mbed_tools.detect.linux


class LinuxTestCase(unittest.TestCase):
    '''Test cases for the Linux-specific detect functions
    '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    mount_list = [
        b'/dev/sdc on /media/usb1 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)',
        b'/dev/sdd on /media/usb2 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)',
        b'/dev/sde on /media/usb3 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)',
        b'/dev/sdf on /media/usb4 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)',
        b'/dev/sdg on /media/usb5 type vfat (rw,noexec,nodev,sync,noatime,nodiratime,gid=1000,uid=1000,dmask=000,fmask=000)',
        b'/dev/sdh on /media/mbed/DAPLINK type vfat (rw,nosuid,nodev,relatime,uid=1000,gid=1000,fmask=0022,dmask=0022,codepage=437,iocharset=iso8859-1,shortname=mixed,showexec,utf8,flush,errors=remount-ro,uhelper=udisks2)'
    ]

    listdir_dict = {
        '/dev/disk/by-id': [
            'usb-MBED_VFS_0240000028634e4500135006691700105f21000097969900-0:0', # sdb, unmounted
            'usb-MBED_VFS_0240000033514e45001f500585d40014e981000097969900-0:0', # sdc, pci prefixed serial
            'usb-MBED_VFS_0240000029164e45002f0012706e0006f301000097969900-0:0', # sdd, no serial-by-id listing
            'usb-MBED_VFS_9900000031864e45000a100e0000003c0000000097969901-0:0', # sde, 9900 target id, microbit
            'usb-MBED_FDi_sk_A000000001-0:0',                                    # sdf, very short target id, different usb string
            'usb-MBED_microcontroller_0672FF485649785087171742-0:0',             # sdg, shorter target id, stlink
            'usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0'              # sdh, shorter target id
        ],
        '/dev/serial/by-id': [
            'usb-ARM_DAPLink_CMSIS-DAP_0240000028634e4500135006691700105f21000097969900-if01',
            'usb-ARM_BBC_micro:bit_CMSIS-DAP_9900000031864e45000a100e0000003c0000000097969901-if01',
            'usb-MBED_MBED_CMSIS-DAP_A000000001-if01',
            'usb-MBED_MBED_CMSIS-DAP_0240020152986E5EAF6693E6-if01',
            'pci-ARM_DAPLink_CMSIS-DAP_0240000033514e45001f500585d40014e981000097969900-if01',
            'usb-STMicroelectronics_STM32_STLink_0672FF485649785087171742-if02'
        ],
        '/sys/class/block': [
            'sdb',
            'sdc',
            'sdd',
            'sde',
            'sdf',
            'sdg',
            'sdh'
        ],
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-1/1-1.2/1-1.2.6': [
            'idVendor',
            'idProduct'
        ],
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-2': [
            'idVendor',
            'idProduct'
        ],
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-3': [
            'idVendor',
            'idProduct'
        ],
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-4': [
            'idVendor',
            'idProduct'
        ],
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-5': [
            'idVendor',
            'idProduct'
        ],
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-6': [
            'idVendor',
            'idProduct'
        ],
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-7': [
            'idVendor',
            'idProduct'
        ]
    }

    open_dict = {
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-1/1-1.2/1-1.2.6/idVendor': '0d28\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-1/1-1.2/1-1.2.6/idProduct': '0204\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-2/idVendor': '0d28\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-2/idProduct': '0204\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-3/idVendor': '0d28\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-3/idProduct': '0204\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-4/idVendor': '0d28\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-4/idProduct': '0204\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-5/idVendor': '0d28\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-5/idProduct': '0204\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-6/idVendor': '0483\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-6/idProduct': '374b\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-7/idVendor': '0d28\n',
        '/sys/class/block/../../devices/pci0000:00/0000:00:06.0/usb1/1-7/idProduct': '0204\n'
    }

    link_dict = {
        # Disks
        '/dev/disk/by-id/usb-MBED_VFS_0240000028634e4500135006691700105f21000097969900-0:0': '../../sdb',
        '/dev/disk/by-id/usb-MBED_FDi_sk_A000000001-0:0': '../../sdf',
        '/dev/disk/by-id/usb-MBED_VFS_9900000031864e45000a100e0000003c0000000097969901-0:0': '../../sde',
        '/dev/disk/by-id/usb-MBED_VFS_0240000029164e45002f0012706e0006f301000097969900-0:0': '../../sdd', # No serial-by-id listing
        '/dev/disk/by-id/usb-MBED_VFS_0240000033514e45001f500585d40014e981000097969900-0:0': '../../sdc', # wierd pci serial one
        '/dev/disk/by-id/usb-MBED_microcontroller_0672FF485649785087171742-0:0': '../../sdg',
        '/dev/disk/by-id/usb-MBED_microcontroller_0240020152986E5EAF6693E6-0:0': '../../sdh',

        # Serial
        '/dev/serial/by-id/usb-ARM_DAPLink_CMSIS-DAP_0240000028634e4500135006691700105f21000097969900-if01': '../../ttyACM0',
        '/dev/serial/by-id/usb-ARM_BBC_micro:bit_CMSIS-DAP_9900000031864e45000a100e0000003c0000000097969901-if01': '../../ttyACM1',
        '/dev/serial/by-id/usb-MBED_MBED_CMSIS-DAP_0240020152986E5EAF6693E6-if01': '../../ttyACM2',
        '/dev/serial/by-id/usb-MBED_MBED_CMSIS-DAP_A000000001-if01': '../../ttyACM3',
        '/dev/serial/by-id/pci-ARM_DAPLink_CMSIS-DAP_0240000033514e45001f500585d40014e981000097969900-if01': '../../ttyACM5',
        '/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_0672FF485649785087171742-if02': '../../ttyACM4',

        # sysfs
        '/sys/class/block/sdb': '../../devices/pci0000:00/0000:00:06.0/usb1/1-2/1-2:1.0/host3/target3:0:0/3:0:0:0/block/sdb',
        '/sys/class/block/sdc': '../../devices/pci0000:00/0000:00:06.0/usb1/1-3/1-3:1.0/host4/target4:0:0/4:0:0:0/block/sdc',
        '/sys/class/block/sdd': '../../devices/pci0000:00/0000:00:06.0/usb1/1-4/1-4:1.0/host5/target5:0:0/5:0:0:0/block/sdd',
        '/sys/class/block/sde': '../../devices/pci0000:00/0000:00:06.0/usb1/1-1/1-1.2/1-1.2.6/1-1.2.6:1.0/host8568/target8568:0:0/8568:0:0:0/block/sde',
        '/sys/class/block/sdf': '../../devices/pci0000:00/0000:00:06.0/usb1/1-5/1-5:1.0/host6/target6:0:0/7:0:0:0/block/sdf',
        '/sys/class/block/sdg': '../../devices/pci0000:00/0000:00:06.0/usb1/1-6/1-6:1.0/host7/target7:0:0/8:0:0:0/block/sdg',
        '/sys/class/block/sdh': '../../devices/pci0000:00/0000:00:06.0/usb1/1-7/1-7:1.0/host8/target8:0:0/9:0:0:0/block/sdh'
    }

    def test_find_usb_devices(self):

        if not getattr(sys.modules['os'], 'readlink', None):
            sys.modules['os'].readlink = None

        def do_open(path, mode='r'):
            path = path.replace('\\', '/')
            file_object = mock_open(read_data=self.open_dict[path]).return_value
            file_object.__iter__.return_value = self.open_dict[path].splitlines(True)
            return file_object

        with patch('mbed_tools.detect.linux._run_cli_process') as _cliproc,\
             patch('os.readlink') as _readlink,\
             patch('os.listdir') as _listdir,\
             patch('mbed_tools.detect.linux.abspath') as _abspath,\
             patch('mbed_tools.detect.linux.open', do_open) as _,\
             patch('mbed_tools.detect.linux.isdir') as _isdir:
            _isdir.return_value = True
            _cliproc.return_value = (b'\n'.join(self.mount_list), None, 0)
            def do_readlink(link):
                # Fix for testing on Windows
                link = link.replace('\\', '/')
                return self.link_dict[link]
            _readlink.side_effect = do_readlink
            def do_listdir(dir):
                # Fix for testing on Windows
                dir = dir.replace('\\', '/')
                return self.listdir_dict[dir]
            _listdir.side_effect = do_listdir
            def do_abspath(dir):
                _, path = os.path.splitdrive(
                    os.path.normpath(os.path.join(os.getcwd(), dir)))
                path = path.replace('\\', '/')
                return path
            _abspath.side_effect = do_abspath

            usb_devices = mbed_tools.detect.linux.find_usb_devices()

            expected = {
               '0240000028634e4500135006691700105f21000097969900': {
                    'vendor_id': '0d28',
                    'product_id': '0204',
                    'mount_point': None,
                    'serial_port': '/dev/ttyACM0'
                },
                '0240000033514e45001f500585d40014e981000097969900': {
                    'vendor_id': '0d28',
                    'product_id': '0204',
                    'mount_point': '/media/usb1',
                    'serial_port': '/dev/ttyACM5'
                },
                '0240000029164e45002f0012706e0006f301000097969900': {
                    'vendor_id': '0d28',
                    'product_id': '0204',
                    'mount_point': '/media/usb2',
                    'serial_port': None
                },
                '9900000031864e45000a100e0000003c0000000097969901': {
                    'vendor_id': '0d28',
                    'product_id': '0204',
                    'mount_point': '/media/usb3',
                    'serial_port': '/dev/ttyACM1'
                },
                'A000000001': {
                    'vendor_id': '0d28',
                    'product_id': '0204',
                    'mount_point': '/media/usb4',
                    'serial_port': '/dev/ttyACM3'
                },
                '0672FF485649785087171742': {
                    'vendor_id': '0483',
                    'product_id': '374b',
                    'mount_point': '/media/usb5',
                    'serial_port': '/dev/ttyACM4'
                },
                '0240020152986E5EAF6693E6': {
                    'vendor_id': '0d28',
                    'product_id': '0204',
                    'mount_point': '/media/mbed/DAPLINK',
                    'serial_port': '/dev/ttyACM2'
                }
            }

            found_usb_ids = set()
            for usb_device in usb_devices:
                found_usb_ids.add(usb_device.usb_id)
                expected_device = expected[usb_device.usb_id]
                self.assertEqual(usb_device.vendor_id, expected_device['vendor_id'], usb_device.usb_id)
                self.assertEqual(usb_device.product_id, expected_device['product_id'], usb_device.usb_id)

            self.assertEqual(found_usb_ids, set(expected.keys()))
            _cliproc.assert_not_called()

            for usb_device in usb_devices:
                _cliproc.reset_mock()
                expected_device = expected[usb_device.usb_id]
                self.assertEqual(usb_device.mount_point(), expected_device['mount_point'], usb_device.usb_id)
                if expected_device['mount_point']:
                    _cliproc.assert_called_with('mount')

                self.assertEqual(usb_device.serial_port(), expected_device['serial_port'], usb_device.usb_id)
