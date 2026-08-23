"""YwRobot 진동모터 2개를 제어하는 파일.

현재 확인된 동작 방식:
- GPIO 값 1 = 진동 ON
- GPIO 값 0 = 진동 OFF

현재 연결:
- 왼쪽 진동모터: GPIO36, 물리 Pin 11
- 오른쪽 진동모터: GPIO39, 물리 Pin 13

이 모듈은 디지털 입력 방식이라 실제 전압 기반 세기 조절은 하지 않는다.
대신 짧게 켰다 껐다 반복하는 방식으로 약한 진동/강한 진동 패턴을 만든다.
"""

import atexit
import time
from pathlib import Path


PATTERN_STRAIGHT = "straight"
PATTERN_PREPARE_LEFT = "prepare_left"
PATTERN_PREPARE_RIGHT = "prepare_right"
PATTERN_LEFT = "left"
PATTERN_RIGHT = "right"
PATTERN_FRONT_OBSTACLE = "front_obstacle"
PATTERN_LEFT_OBSTACLE = "left_obstacle"
PATTERN_RIGHT_OBSTACLE = "right_obstacle"
PATTERN_OCR_SEARCHING = "ocr_searching"
PATTERN_ARRIVED = "arrived"
PATTERN_NETWORK_ERROR = "network_error"
PATTERN_ERROR = "error"


SYSFS_GPIO_PATH = Path("/sys/class/gpio")

ON_VALUE = "1"
OFF_VALUE = "0"


def _write_text(path: Path, value: str) -> None:
    path.write_text(value)


class SysfsGpioOutput:
    def __init__(self, gpio_number: int):
        self.gpio_number = gpio_number
        self.gpio_path = SYSFS_GPIO_PATH / f"gpio{gpio_number}"

    def setup(self):
        if not self.gpio_path.exists():
            _write_text(SYSFS_GPIO_PATH / "export", str(self.gpio_number))
            time.sleep(0.1)

        _write_text(self.gpio_path / "direction", "out")
        self.off()

    def on(self):
        _write_text(self.gpio_path / "value", ON_VALUE)

    def off(self):
        if self.gpio_path.exists():
            _write_text(self.gpio_path / "value", OFF_VALUE)

    def pulse(self, on_time: float, off_time: float, count: int):
        for _ in range(count):
            self.on()
            time.sleep(on_time)
            self.off()
            time.sleep(off_time)

    def vibrate(self, duration: float, intensity: float = 1.0):
        intensity = max(0.1, min(1.0, intensity))

        if intensity >= 0.9:
            self.on()
            time.sleep(duration)
            self.off()
            return

        if intensity >= 0.6:
            self.pulse(on_time=0.08, off_time=0.04, count=max(1, int(duration / 0.12)))
            return

        if intensity >= 0.3:
            self.pulse(on_time=0.05, off_time=0.08, count=max(1, int(duration / 0.13)))
            return

        self.pulse(on_time=0.03, off_time=0.12, count=max(1, int(duration / 0.15)))

    def force_off(self):
        if not self.gpio_path.exists():
            _write_text(SYSFS_GPIO_PATH / "export", str(self.gpio_number))
            time.sleep(0.1)

        _write_text(self.gpio_path / "direction", "out")

        for _ in range(5):
            self.off()
            time.sleep(0.03)

    def cleanup(self):
        self.force_off()


class VibrationMotorController:
    def __init__(self, left_pin: int = 36, right_pin: int = 39, intensity: float = 0.45):
        self.left_motor = SysfsGpioOutput(left_pin)
        self.right_motor = SysfsGpioOutput(right_pin)
        self.intensity = intensity
        self.is_setup = False
        atexit.register(self.cleanup)

    def setup(self):
        self.left_motor.setup()
        self.right_motor.setup()
        self.force_stop_all()
        self.is_setup = True

    def stop_all(self):
        self.left_motor.off()
        self.right_motor.off()

    def force_stop_all(self):
        self.left_motor.force_off()
        self.right_motor.force_off()

    def vibrate_left(self, duration: float = 0.3, intensity: float | None = None):
        self.left_motor.vibrate(duration, intensity or self.intensity)

    def vibrate_right(self, duration: float = 0.3, intensity: float | None = None):
        self.right_motor.vibrate(duration, intensity or self.intensity)

    def vibrate_both(self, duration: float = 0.3, intensity: float | None = None):
        intensity = intensity or self.intensity
        start_time = time.time()

        if intensity >= 0.9:
            self.left_motor.on()
            self.right_motor.on()
            time.sleep(duration)
            self.stop_all()
            return

        if intensity >= 0.6:
            on_time = 0.08
            off_time = 0.04
        elif intensity >= 0.3:
            on_time = 0.05
            off_time = 0.08
        else:
            on_time = 0.03
            off_time = 0.12

        while time.time() - start_time < duration:
            self.left_motor.on()
            self.right_motor.on()
            time.sleep(on_time)
            self.stop_all()
            time.sleep(off_time)

        self.stop_all()

    def play_pattern(self, pattern: str):
        if not self.is_setup:
            raise RuntimeError("VibrationMotorController is not set up")

        try:
            if pattern == PATTERN_STRAIGHT:
                self.vibrate_both(0.15, 0.3)

            elif pattern == PATTERN_PREPARE_LEFT:
                self.vibrate_left(0.15, 0.3)
                time.sleep(0.15)
                self.vibrate_left(0.15, 0.3)

            elif pattern == PATTERN_PREPARE_RIGHT:
                self.vibrate_right(0.15, 0.3)
                time.sleep(0.15)
                self.vibrate_right(0.15, 0.3)

            elif pattern == PATTERN_LEFT:
                self.vibrate_left(0.45, 0.5)

            elif pattern == PATTERN_RIGHT:
                self.vibrate_right(0.45, 0.5)

            elif pattern == PATTERN_FRONT_OBSTACLE:
                for _ in range(3):
                    self.vibrate_both(0.12, 0.9)
                    time.sleep(0.08)

            elif pattern == PATTERN_LEFT_OBSTACLE:
                for _ in range(3):
                    self.vibrate_left(0.12, 0.9)
                    time.sleep(0.08)

            elif pattern == PATTERN_RIGHT_OBSTACLE:
                for _ in range(3):
                    self.vibrate_right(0.12, 0.9)
                    time.sleep(0.08)

            elif pattern == PATTERN_OCR_SEARCHING:
                self.vibrate_both(0.08, 0.3)
                time.sleep(0.08)
                self.vibrate_both(0.08, 0.3)

            elif pattern == PATTERN_ARRIVED:
                for _ in range(2):
                    self.vibrate_both(0.35, 0.6)
                    time.sleep(0.2)

            elif pattern == PATTERN_NETWORK_ERROR:
                self.vibrate_left(0.1, 0.6)
                time.sleep(0.1)
                self.vibrate_right(0.1, 0.6)
                time.sleep(0.1)
                self.vibrate_left(0.1, 0.6)
                time.sleep(0.1)
                self.vibrate_right(0.1, 0.6)

            elif pattern == PATTERN_ERROR:
                for _ in range(4):
                    self.vibrate_both(0.08, 0.9)
                    time.sleep(0.08)

            else:
                self.stop_all()

        finally:
            self.force_stop_all()

    def cleanup(self):
        self.force_stop_all()
        self.is_setup = False