from abc import ABC, abstractmethod
from enum import Enum
from typing import List
import time
import datetime
from ctypes import memset
# import libusb1  # You may need to install the 'pyusb' library for this import
# import DmxDevice from dmx_device
from dmx_device import DmxDevice
import usb.core
import usb.util

class DmxDeviceEurolitePro(DmxDevice):
    FTDI_VENDOR_ID = 0x0403
    FTDI_PRODUCT_ID = 0x6001

    def __init__(self):
        super().__init__()
        self.devh = None
        self.dev = None
        self.channels_to_write = []
        self.dmx_frame = bytearray(518)
        self.data_changed = False
        self.device_status = DmxDevice.DeviceStatus.NOT_STARTED
        self.last_time_of_write = datetime.datetime.now()

    def update_channel_value(self, channel, value):
        # print(f'Setting channel {channel} to {value} (previous value: {self.dmx_frame[channel + 4]})')
        self.dmx_frame[channel + 4] = value
        # self.write_complete_data()

    def write_data(self, channels_to_write, max_channel):
        print("writing")
        for i in range(max_channel):
            self.dmx_frame[i + 4] = channels_to_write[i]

        for value in self.dmx_frame:
            print(str(value))

        self.devh.write(0x2 | usb.ENDPOINT_OUT, bytes(self.dmx_frame), timeout=0)
        print("done.")
        return 0

    def write_complete_data(self):
        # print("write_complete_data")
        # time_since_last_write = datetime.datetime.now() - self.last_time_of_write
        # while time_since_last_write.microseconds / 1000 < 25:
        #     time.sleep(0.01)
        #     time_since_last_write = datetime.datetime.now() - self.last_time_of_write
        self.devh.write(0x2 | usb.ENDPOINT_OUT, bytes(self.dmx_frame), timeout=0)
        return 0

    def start_device(self):
        print('Now in start_device()')
        if self.device_already_started():
            print("DmxDevice was already started")
        else:
            status = 0
            ctx = None
            status = usb.core.find(idVendor=self.FTDI_VENDOR_ID, idProduct=self.FTDI_PRODUCT_ID)
            if status is None:
                print("DMX interface not found.")
                return status

            self.devh = status
            if self.devh:
                print("opened Eurolite Pro DMX interface")
                self.device_status = self.DeviceStatus.STARTED

                divisor = 3000000 / 250000
                value = int(divisor)  # Convert to integer
                index = (int(divisor) >> 8) & 0xFF00  # Convert to integer before shifting
                self.devh.ctrl_transfer(
                    usb.TYPE_VENDOR | usb.RECIP_DEVICE | usb.ENDPOINT_OUT,
                    0x03,
                    value,
                    index,
                    None,
                    0
                )
                print("Set Baud Rate of Eurolite Pro.")

                self.dmx_frame[0] = 0x7e
                self.dmx_frame[1] = 6
                self.dmx_frame[2] = 0b00000001
                self.dmx_frame[3] = 0b00000010
                self.dmx_frame[4] = 0
                # Use slicing to set the values from index 5 to 516 (inclusive) to 0
                self.dmx_frame[5:517] = bytes([0] * 512)
                self.dmx_frame[517] = 0xe7
            else:
                print("could not open DMX interface. error id:", status)
                return status

            return 0

    def device_already_started(self):
        return (
            self.device_status == self.DeviceStatus.STARTED
            or self.device_status == self.DeviceStatus.WAIT_FOR_DATA
            or self.device_status == self.DeviceStatus.STOPPED
        )

    def stop_device(self):
        self.device_status = self.DeviceStatus.STOPPED
        return 0

    def is_connected(self):
        status = usb.core.find(idVendor=self.FTDI_VENDOR_ID, idProduct=self.FTDI_PRODUCT_ID)
        return status is not None

    def start_daemon_thread(self):
        pass  # Eurolite does not use a daemon thread

    def turn_off_all_channels(self, pan_tilt_channels):
        actual = 0
        memset(self.dmx_frame + 5, 0, 512)
        for i in range(len(pan_tilt_channels)):
            self.dmx_frame[4 + pan_tilt_channels[i]] = 127

        self.devh.write(0x2 | usb.ENDPOINT_OUT, bytes(self.dmx_frame), timeout=0)
        time.sleep(0.025)
        return 0

    def set_all_channel_values(self, channels_with_default_values, only_non_zeros):
        actual = 0
        for i in range(512):
            if i < len(channels_with_default_values):
                if only_non_zeros:
                    if channels_with_default_values[i] > 0:
                        self.dmx_frame[i + 5] = channels_with_default_values[i]
                else:
                    self.dmx_frame[i + 5] = channels_with_default_values[i]

        self.devh.write(0x2 | usb.ENDPOINT_OUT, bytes(self.dmx_frame), timeout=0)
        time.sleep(0.025)

        if only_non_zeros:
            time.sleep(4)
            for i in range(512):
                if i < len(channels_with_default_values):
                    if channels_with_default_values[i] > 0:
                        self.dmx_frame[i + 5] = 0

            self.devh.write(0x2 | usb.ENDPOINT_OUT, bytes(self.dmx_frame), timeout=0)
        return 0
