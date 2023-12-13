from abc import ABC, abstractmethod
from enum import Enum
from typing import List
# import time
# from ctypes import memset
# import libusb1  # You may need to install the 'pyusb' library for this import


class DmxDevice(ABC):
    class DeviceStatus(Enum):
        NOT_STARTED = 0
        STARTED = 1
        WAIT_FOR_DATA = 2
        STOPPED = 3

    @abstractmethod
    def write_data(self, channels_to_write: List[int], max_channel: int) -> int:
        pass

    @abstractmethod
    def write_complete_data(self) -> int:
        pass

    @abstractmethod
    def start_device(self) -> int:
        pass

    @abstractmethod
    def stop_device(self) -> int:
        pass

    def set_device_status(self, device_status):
        self.device_status = device_status

    @abstractmethod
    def turn_off_all_channels(self, pan_tilt_channels: List[int]) -> int:
        pass

    @abstractmethod
    def set_all_channel_values(self, channels_with_default_values: List[int], only_non_zeros: bool) -> int:
        pass

    @abstractmethod
    def start_daemon_thread(self):
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    def __del__(self):
        pass  # Cleanup code, if any
