import os
import copy

class MbedDevice(object):
    '''Class for representing an Mbed device'''

    DETAILS_TXT_NAME = 'DETAILS.TXT'
    MBED_HTM_NAME = 'mbed.htm'
    _VENDOR_ID_DEVICE_TYPE_MAP = {
        '03eb': 'atmel',
        '0483': 'stlink',
        '0d28': 'daplink',
        '1366': 'jlink'
    }
    # Public methods and properties
    def __init__(self, usb_device, platform_database=None):
        '''Create an MbedDevice from a UsbDevice

        @param usb_device The UsbDevice instance that represents the MbedDevice
        '''
        self._usb_device = usb_device
        self._directory_entries = []

        self._match(platform_database)

    @property
    def directory_entries(self):
        return self._directory_entries

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

    @property
    def _detect_device_type(self, device):
        return self.VENDOR_ID_DEVICE_TYPE_MAP.get(device.get('vendor_id'))

    def update(self, platform_database=None):
        '''Update the cached values for the Mbed Device

        This will use the UsbDevice to query the system for information about
        this device.
        '''
        self._usb_device.update()
        self._match(platform_database)

    def _match(self, platform_database=None):
        if platform_database:
            self._platform_databse = platform_database

        self._target_id = self._usb_device.id
        identifier = None

        if self.mount_point:
            try:
                self._directory_entries = os.listdir(self.mount_point)

                # Always try to update using daplink compatible boards process.
                # This is done for backwards compatibility.
                self._update_device_details_daplink_compatible()

                if self.device_type == 'jlink':
                    identifier = self._update_device_details_jlink()
                elif self.device_type == 'atmel':
                    self._update_device_details_atmel()

            except (OSError, IOError) as e:
                logger.warning(
                    'Marking device with mount point "%s" as unmounted due to the '
                    'following error: %s', self.mount_point, e)
                # TODO fix this logger and dismount thing
                # device['mount_point'] = None

        # For now, daplink and stlink share a platform database
        plat_device_type = self.device_type or 'daplink'
        if plat_device_type == 'stlink':
            plat_device_type = 'daplink'

        identifier = indentifier if identifier else self._target_id[0:4]

        # Get the details from the platform database
        platform_data = copy.copy(self.plat_db.get(
            indentifier, device_type=plat_device_type, verbose_data=True
        )) or {"platform_name": None}

        # Add remainder details to the device details
        device._platform_name = platform_data['platform_name']
        del platform_data['platform_name']
        self._device_details.update(platform_data)

    def _update_device_details_daplink_compatible(self):
        ''' Updates the daplink-specific device information based on files from its 'mount_point'
        '''
        lowercase_directory_entries = [e.lower() for e in self._directory_entries]
        if self.MBED_HTM_NAME.lower() in lowercase_directory_entries:
            self._update_device_from_htm()

        if self.DETAILS_TXT_NAME.lower() in lowercase_directory_entries:
            details_txt = self._details_txt() or {}
            self._device_details.update({"daplink_%s" % f.lower().replace(' ', '_'): v
                           for f, v in details_txt.items()})

            # If details.txt contains the target id, this is the most trusted source
            self._target_id = details_txt.get('daplink_unique_id', self._target_id):

    def _update_device_details_jlink(self):
        ''' Updates the jlink-specific device information based on files from its mount_point'''
        lower_case_map = {e.lower(): e for e in self._directory_entries}

        if 'board.html' in lower_case_map:
            board_file_key = 'board.html'
        elif 'user guide.html' in lower_case_map:
            board_file_key = 'user guide.html'
        else:
            logger.warning('No valid file found to update JLink device details')
            return

        board_file_path = os.path.join(self._mount_point, lower_case_map[board_file_key])
        with open(board_file_path, 'r') as board_file:
            board_file_lines = board_file.readlines()

        # For jlink, the target id isn't used as the index into the platform database, an
        # identifier from the device's filesystem is used instead. This returns that identifier.
        for line in board_file_lines:
            m = re.search(r'url=([\w\d\:\-/\\\?\.=-_]+)', line)
            if m:
                self._url = m.group(1).strip()
                return self._url.split('/')[-1]

    def _update_device_details_atmel(self):
        '''Updates the Atmel device information based on files from its mount point'''
        # Atmel uses a system similar to DAPLink, but there's no details.txt with a target ID
        # to identify device we can use the serial, which is ATMLXXXXYYYYYYY
        # where XXXX is the board identifier.
        # This can be verified by looking at readme.htm, which also uses the board ID to redirect to platform page

        self._target_id = self._usb_device.id[4:]

    def _update_device_from_htm(self):
        '''Set the 'target_id', 'target_id_mbed_htm', 'platform_name' and
        'daplink_*' attributes by reading from mbed.htm on the device
        '''
        htm_target_id, daplink_info = self._read_htm_ids()
        if daplink_info:
            self._device_details.update({"daplink_%s" % f.lower().replace(' ', '_'): v
                           for f, v in daplink_info.items()})
        if htm_target_id:
            logger.debug("Found htm target id, %s, for usb target id %s",
                            htm_target_id, self._usb_device.id)
            self._target_id = htm_target_id
        else:
            logger.debug("Could not read htm on from usb id %s. "
                            "Falling back to usb id",
                            self._usb_device.id)
        self._device_details['target_id_mbed_htm'] = htm_target_id

    def _read_htm_ids(self):
        ''' Function scans mbed.htm to get information about TargetID.
        @return Function returns targetID, in case of failure returns None.
        @details Note: This function should be improved to scan variety of boards' mbed.htm files
        '''
        result = {}
        target_id = None
        for line in self._htm_lines():
            target_id = target_id or self._target_id_from_htm(line)
            ver_bld = self._mbed_htm_comment_section_ver_build(line)
            if ver_bld:
                result['version'], result['build'] = ver_bld

            m = re.search(r'url=([\w\d\:/\\\?\.=-_]+)', line)
            if m:
                result['url'] = m.group(1).strip()
        return target_id, result

    def _mbed_htm_comment_section_ver_build(self, line):
        ''' Check for Version and Build date of interface chip firmware im mbed.htm file
        @return (version, build) tuple if successful, None if no info found
        '''
        # <!-- Version: 0200 Build: Mar 26 2014 13:22:20 -->
        m = re.search(r'^<!-- Version: (\d+) Build: ([\d\w: ]+) -->', line)
        if m:
            version_str, build_str = m.groups()
            return (version_str.strip(), build_str.strip())

        # <!-- Version: 0219 Build: Feb  2 2016 15:20:54 Git Commit SHA: 0853ba0cdeae2436c52efcba0ba76a6434c200ff Git local mods:No-->
        m = re.search(r'^<!-- Version: (\d+) Build: ([\d\w: ]+) Git Commit SHA', line)
        if m:
            version_str, build_str = m.groups()
            return (version_str.strip(), build_str.strip())

        # <!-- Version: 0.14.3. build 471 -->
        m = re.search(r'^<!-- Version: ([\d+\.]+)\. build (\d+) -->', line)
        if m:
            version_str, build_str = m.groups()
            return (version_str.strip(), build_str.strip())
        return None

    def _htm_lines(self):
        mbed_htm_path = join(self.mount_point, self.MBED_HTM_NAME)
        with open(mbed_htm_path, 'r') as f:
            return f.readlines()

    def _details_txt(self):
        ''' Load DETAILS.TXT to dictionary:
            DETAILS.TXT example:
            Version: 0226
            Build:   Aug 24 2015 17:06:30
            Git Commit SHA: 27a236b9fe39c674a703c5c89655fbd26b8e27e1
            Git Local mods: Yes

            or:

            # DAPLink Firmware - see https://mbed.com/daplink
            Unique ID: 0240000029164e45002f0012706e0006f301000097969900
            HIF ID: 97969900
            Auto Reset: 0
            Automation allowed: 0
            Daplink Mode: Interface
            Interface Version: 0240
            Git SHA: c765cbb590f57598756683254ca38b211693ae5e
            Local Mods: 0
            USB Interfaces: MSD, CDC, HID
            Interface CRC: 0x26764ebf
        '''
        path_to_details_txt = os.path.join(self.mount_point, self.DETAILS_TXT_NAME)
        with open(path_to_details_txt, 'r') as f:
            return self._parse_details(f.readlines())

    def _parse_details(self, lines):
        result = {}
        for line in lines:
            if not line.startswith('#'):
                key, _, value = line.partition(':')
                if value:
                    result[key] = value.strip()
        if 'Interface Version' in result:
            result['Version'] = result['Interface Version']
        return result

    def _target_id_from_htm(self, line):
        ''' Extract Target id from htm line.
        @return Target id or None
        '''
        # Detecting modern mbed.htm file format
        m = re.search('\?code=([a-fA-F0-9]+)', line)
        if m:
            result = m.groups()[0]
            logger.debug("Found target id %s in htm line %s", result, line)
            return result
        # Last resort, we can try to see if old mbed.htm format is there
        m = re.search('\?auth=([a-fA-F0-9]+)', line)
        if m:
            result = m.groups()[0]
            logger.debug("Found target id %s in htm line %s", result, line)
            return result

        return None
