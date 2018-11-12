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

import re
from os.path import join, isdir, dirname, abspath
import os

from . import UsbDevice
from mbed_tools.utils import _run_cli_process

import logging
logger = logging.getLogger("mbed_tools.detect.linux")
logger.addHandler(logging.NullHandler())
del logging

_SYSFS_BLOCK_DEVICE_PATH = '/sys/class/block'
_NAME_LINK_PATTERN = re.compile(
    r'(pci|usb)-[0-9a-zA-Z:_-]*_(?P<usbid>[0-9a-zA-Z]*)-.*$')
_MOUNT_MEDIA_PATTERN = re.compile(
    r'(?P<dev>(/[^/ ]*)+) on (?P<dir>(/[^/ ]*)+) ')
_USB_DEVICE_PATTERN = re.compile(r'^[0-9]+-[0-9]+[^:\s]*$')

def _readlink(link):
    content = os.readlink(link)
    if content.startswith(".."):
        return abspath(join(dirname(link), content))
    else:
        return content

def _hex_ids(dev_list):
    """! Build a USBID map for a device list
    @param disk_list List of disks in a system with USBID decoration
    @return Returns map USBID -> device file in /dev
    @details Uses regular expressions to get a USBID (TargeTIDs) a "by-id"
      symbolic link
    """
    logger.debug("Converting device list %r", dev_list)
    for dl in dev_list:
        match = _NAME_LINK_PATTERN.search(dl)
        if match:
            yield match.group("usbid"), _readlink(dl)

def _dev_by_id(device_type):
    """! Get a dict, USBID -> device, for a device class
    @param device_type The type of devices to search. For exmaple, "serial"
      looks for all serial devices connected to this computer
    @return A dict: Device USBID -> device file in /dev
    """
    dir = join("/dev", device_type, "by-id")
    if isdir(dir):
        to_ret = dict(_hex_ids([join(dir, f) for f in os.listdir(dir)]))
        logger.debug("Found %s devices by id %r", device_type, to_ret)
        return to_ret
    else:
        logger.error("Could not get %s devices by id. "
                     "This could be because your Linux distribution "
                     "does not use udev, or does not create /dev/%s/by-id "
                     "symlinks. Please submit an issue to github.com/"
                     "armmbed/mbed-ls.", device_type, device_type)
        return {}

def _fat_mounts():
    """! Lists mounted devices with vfat file system (potential mbeds)
    @result Returns list of all mounted vfat devices
    @details Uses Linux shell command: 'mount'
    """
    _stdout, _, retval = _run_cli_process('mount')
    if not retval:
        for line in _stdout.splitlines():
            if b'vfat' in line:
                match = _MOUNT_MEDIA_PATTERN.search(line.decode('utf-8'))
                if match:
                    yield match.group("dev"), match.group("dir")

def _sysfs_block_devices(block_devices):
    device_names = { os.path.basename(d): d  for d in block_devices }
    sysfs_block_devices = set(os.listdir(_SYSFS_BLOCK_DEVICE_PATH))
    common_device_names = sysfs_block_devices.intersection(set(device_names.keys()))
    result = {}

    for common_device_name in common_device_names:
        sysfs_path = os.path.join(_SYSFS_BLOCK_DEVICE_PATH, common_device_name)
        full_sysfs_path = os.readlink(sysfs_path)
        path_parts = full_sysfs_path.split('/')

        end_index = None
        for index, part in enumerate(path_parts):
            if _USB_DEVICE_PATTERN.search(part):
                end_index = index

        if end_index == None:
            logger.debug('Did not find suitable usb folder for usb info: %s', full_sysfs_path)
            continue

        usb_info_rel_path = path_parts[:end_index + 1]
        usb_info_path = os.path.join(_SYSFS_BLOCK_DEVICE_PATH, os.sep.join(usb_info_rel_path))

        vendor_id = None
        product_id = None

        vendor_id_file_paths = os.path.join(usb_info_path, 'idVendor')
        product_id_file_paths = os.path.join(usb_info_path, 'idProduct')

        try:
            with open(vendor_id_file_paths, 'r') as vendor_file:
                vendor_id = vendor_file.read().strip()
        except OSError as e:
            logger.debug('Failed to read vendor id file %s weith error:', vendor_id_file_paths, e)

        try:
            with open(product_id_file_paths, 'r') as product_file:
                product_id = product_file.read().strip()
        except OSError as e:
            logger.debug('Failed to read product id file %s weith error:', product_id_file_paths, e)

        result[device_names[common_device_name]] = {
            'vendor_id': vendor_id,
            'product_id': product_id
        }

    return result


class LinuxUsbDevice(UsbDevice):
    '''Linux implementation for the UsbDevice class'''

    def __init__(self, usb_id, vendor_id, product_id):
        self._usb_id = usb_id
        self._vendor_id = vendor_id
        self._product_id = product_id

        if self._vendor_id is None or self._product_id is None:
            logger.warning('Received incomplete USB data', {
                'usb_id': self._usb_id,
                'vendor_id': self._vendor_id,
                'product_id': self._product_id
            })

    @property
    def usb_id(self):
        return self._usb_id

    @property
    def vendor_id(self):
        return self._vendor_id

    @property
    def product_id(self):
        return self._product_id

    def mount_point(self):
        mount_point = None
        disk_name = _dev_by_id('disk').get(self._usb_id)
        if disk_name:
            mount_point = dict(_fat_mounts()).get(disk_name)
        return mount_point

    def serial_port(self):
        return _dev_by_id('serial').get(self._usb_id)


def find_usb_devices():
    disks = _dev_by_id('disk')
    usb_info = _sysfs_block_devices(disks.values())

    return [
        LinuxUsbDevice(
            usb_id,
            usb_info.get(disk_name, {}).get('vendor_id'),
            usb_info.get(disk_name, {}).get('product_id')
        ) for usb_id, disk_name in disks.items()
    ]
