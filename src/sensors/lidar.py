from __future__ import annotations

import time
from typing import Any


TF_LUNA_UART_HEADER = b"\x59\x59"

TF_LUNA_I2C_DEFAULT_ADDRESS = 0x10
TCA9548A_DEFAULT_ADDRESS = 0x70

MIN_VALID_STRENGTH = 100
OVEREXPOSED_STRENGTH = 65535

DEFAULT_LIDAR_CHANNELS = {
    "front": 0,
    "left": 1,
    "right": 2,
    "upper": 3,
    "lower": 4,
}


def is_valid_measurement(distance_cm: int | None, strength: int | None) -> bool:
    if distance_cm is None or strength is None:
        return False

    if distance_cm <= 0:
        return False

    if strength < MIN_VALID_STRENGTH:
        return False

    if strength == OVEREXPOSED_STRENGTH:
        return False

    return True
   
class TFLunaUartLidar:
    """TF-Luna 1개를 UART로 읽는 클래스."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def connect(self) -> None:
        import serial

        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
        )

        self.serial.reset_input_buffer()

    def close(self) -> None:
        if self.serial is not None and self.serial.is_open:
            self.serial.close()

    def read_frame(self, max_attempts: int = 100) -> dict[str, Any] | None:
        if self.serial is None:
            raise RuntimeError("LiDAR serial is not connected")

        for _ in range(max_attempts):
            first = self.serial.read(1)

            if first != b"\x59":
                continue

            second = self.serial.read(1)

            if second != b"\x59":
                continue

            rest = self.serial.read(7)

            if len(rest) != 7:
                return None

            frame = first + second + rest
            checksum = sum(frame[:8]) & 0xFF

            if checksum != frame[8]:
                return None

            distance_cm = frame[2] + frame[3] * 256
            strength = frame[4] + frame[5] * 256
            temperature_c = (frame[6] + frame[7] * 256) / 8 - 256

            return {
                "distance_cm": distance_cm,
                "strength": strength,
                "temperature_c": temperature_c,
                "valid": is_valid_measurement(distance_cm, strength),
            }

        return None

    def read_distance_cm(self) -> int | None:
        frame = self.read_frame()

        if frame is None:
            return None

        if not frame["valid"]:
            return None

        return frame["distance_cm"]

    def __enter__(self) -> "TFLunaUartLidar":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class TCA9548A:
    """TCA9548A I2C 멀티플렉서 채널 선택 클래스."""

    def __init__(self, bus, address: int = TCA9548A_DEFAULT_ADDRESS):
        self.bus = bus
        self.address = address
        self.current_channel = None

    def select_channel(self, channel: int) -> None:
        if channel < 0 or channel > 7:
            raise ValueError("TCA9548A channel must be 0~7")

        if self.current_channel == channel:
            return

        self.bus.write_byte(self.address, 1 << channel)
        self.current_channel = channel
        time.sleep(0.002)

    def disable_all(self) -> None:
        self.bus.write_byte(self.address, 0x00)
        self.current_channel = None


class TFLunaI2CLidar:
    """TCA9548A 뒤에 연결된 TF-Luna 1개를 I2C로 읽는 클래스."""

    def __init__(
        self,
        bus,
        mux: TCA9548A,
        channel: int,
        address: int = TF_LUNA_I2C_DEFAULT_ADDRESS,
    ):
        self.bus = bus
        self.mux = mux
        self.channel = channel
        self.address = address

    def read_frame(self) -> dict[str, Any] | None:
        self.mux.select_channel(self.channel)

        try:
            data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
        except OSError:
            return None

        if len(data) != 6:
            return None

        distance_cm = data[0] + data[1] * 256
        strength = data[2] + data[3] * 256
        temperature_c = (data[4] + data[5] * 256) / 100

        return {
            "distance_cm": distance_cm,
            "strength": strength,
            "temperature_c": temperature_c,
            "valid": is_valid_measurement(distance_cm, strength),
        }

    def read_distance_cm(self) -> int | None:
        frame = self.read_frame()

        if frame is None:
            return None

        if not frame["valid"]:
            return None

        return frame["distance_cm"]


class MultiTFLunaLidar:
    """TF-Luna 여러 개를 한 번에 관리하는 클래스."""

    def __init__(
        self,
        bus_number: int,
        channels: dict[str, int] | None = None,
        mux_address: int = TCA9548A_DEFAULT_ADDRESS,
        lidar_address: int = TF_LUNA_I2C_DEFAULT_ADDRESS,
    ):
        from smbus2 import SMBus

        self.bus = SMBus(bus_number)
        self.channels = channels or DEFAULT_LIDAR_CHANNELS
        self.mux = TCA9548A(self.bus, mux_address)

        self.lidars = {
            direction: TFLunaI2CLidar(
                bus=self.bus,
                mux=self.mux,
                channel=channel,
                address=lidar_address,
            )
            for direction, channel in self.channels.items()
        }

    def read_all_frames(self) -> dict[str, dict[str, Any] | None]:
        frames = {}

        for direction, lidar in self.lidars.items():
            frames[direction] = lidar.read_frame()

        return frames

    def read_all_distances_cm(self) -> dict[str, int | None]:
        distances = {}

        for direction, lidar in self.lidars.items():
            distances[direction] = lidar.read_distance_cm()

        return distances

    def close(self) -> None:
        self.mux.disable_all()
        self.bus.close()

    def __enter__(self) -> "MultiTFLunaLidar":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()