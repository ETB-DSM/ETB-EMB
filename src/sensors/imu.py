"""MPU6050 IMU 센서에서 움직임 데이터를 읽는 파일.

가속도와 자이로 값을 읽어서 지팡이 기울기, 충격, 넘어짐 감지 등에 사용할
기초 데이터를 제공한다.
"""

import math
import time
from smbus2 import SMBus


PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B

ACCEL_SCALE = 16384.0
GYRO_SCALE = 131.0


class MPU6050:
    def __init__(self, bus_number: int = 2, address: int = 0x68):
        self.bus_number = bus_number
        self.address = address
        self.bus = None

    def connect(self):
        self.bus = SMBus(self.bus_number)
        self.bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        self.bus.write_byte_data(self.address, SMPLRT_DIV, 0x07)
        self.bus.write_byte_data(self.address, CONFIG, 0x03)
        self.bus.write_byte_data(self.address, GYRO_CONFIG, 0x00)
        self.bus.write_byte_data(self.address, ACCEL_CONFIG, 0x00)

    def close(self):
        if self.bus is not None:
            self.bus.close()
            self.bus = None

    def _read_word(self, reg: int):
        if self.bus is None:
            raise RuntimeError("MPU6050 is not connected")

        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        value = (high << 8) | low

        if value >= 0x8000:
            value -= 0x10000

        return value

    def read_accel(self):
        ax = self._read_word(ACCEL_XOUT_H) / ACCEL_SCALE
        ay = self._read_word(ACCEL_XOUT_H + 2) / ACCEL_SCALE
        az = self._read_word(ACCEL_XOUT_H + 4) / ACCEL_SCALE

        return {"x": ax, "y": ay, "z": az}

    def read_gyro(self):
        gx = self._read_word(ACCEL_XOUT_H + 8) / GYRO_SCALE
        gy = self._read_word(ACCEL_XOUT_H + 10) / GYRO_SCALE
        gz = self._read_word(ACCEL_XOUT_H + 12) / GYRO_SCALE

        return {"x": gx, "y": gy, "z": gz}

    def read_temp(self):
        raw = self._read_word(ACCEL_XOUT_H + 6)
        return raw / 340.0 + 36.53

    def get_tilt(self):
        accel = self.read_accel()
        ax = accel["x"]
        ay = accel["y"]
        az = accel["z"]

        pitch = math.degrees(math.atan2(ax, math.sqrt(ay * ay + az * az)))
        roll = math.degrees(math.atan2(ay, math.sqrt(ax * ax + az * az)))

        return {"pitch": pitch, "roll": roll}

    def read_all(self):
        return {
            "accel": self.read_accel(),
            "gyro": self.read_gyro(),
            "temp": self.read_temp(),
            "tilt": self.get_tilt(),
        }