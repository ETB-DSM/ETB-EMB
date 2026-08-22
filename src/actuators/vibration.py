"""YwRobot 진동모터 2개를 제어하는 파일.

YwRobot 진동모터 모듈은 현재 테스트 결과 active-low 방식으로 확인되었다.
즉, GPIO 출력이 LOW일 때 진동이 켜지고 HIGH일 때 꺼진다.
"""

import time
import OPi.GPIO as GPIO


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


class VibrationMotorController:
    def __init__(self, left_pin: int, right_pin: int):
        self.left_pin = left_pin
        self.right_pin = right_pin
        self.is_setup = False

        # 현재 사용하는 YwRobot 모듈은 LOW 입력에서 진동이 켜진다.
        self.on_level = GPIO.LOW
        self.off_level = GPIO.HIGH

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(self.left_pin, GPIO.OUT)
        GPIO.setup(self.right_pin, GPIO.OUT)

        self.is_setup = True
        self.stop_all()

    def _turn_on(self, pin: int):
        GPIO.output(pin, self.on_level)

    def _turn_off(self, pin: int):
        GPIO.output(pin, self.off_level)

    def stop_all(self):
        GPIO.output(self.left_pin, self.off_level)
        GPIO.output(self.right_pin, self.off_level)

    def vibrate_left(self, duration: float = 0.3):
        self._turn_on(self.left_pin)
        time.sleep(duration)
        self._turn_off(self.left_pin)

    def vibrate_right(self, duration: float = 0.3):
        self._turn_on(self.right_pin)
        time.sleep(duration)
        self._turn_off(self.right_pin)

    def vibrate_both(self, duration: float = 0.3):
        self._turn_on(self.left_pin)
        self._turn_on(self.right_pin)
        time.sleep(duration)
        self.stop_all()

    def play_pattern(self, pattern: str):
        if not self.is_setup:
            raise RuntimeError("VibrationMotorController is not set up")

        if pattern == PATTERN_STRAIGHT:
            self.vibrate_both(0.15)

        elif pattern == PATTERN_PREPARE_LEFT:
            self.vibrate_left(0.15)
            time.sleep(0.15)
            self.vibrate_left(0.15)

        elif pattern == PATTERN_PREPARE_RIGHT:
            self.vibrate_right(0.15)
            time.sleep(0.15)
            self.vibrate_right(0.15)

        elif pattern == PATTERN_LEFT:
            self.vibrate_left(0.5)

        elif pattern == PATTERN_RIGHT:
            self.vibrate_right(0.5)

        elif pattern == PATTERN_FRONT_OBSTACLE:
            for _ in range(3):
                self.vibrate_both(0.12)
                time.sleep(0.08)

        elif pattern == PATTERN_LEFT_OBSTACLE:
            for _ in range(3):
                self.vibrate_left(0.12)
                time.sleep(0.08)

        elif pattern == PATTERN_RIGHT_OBSTACLE:
            for _ in range(3):
                self.vibrate_right(0.12)
                time.sleep(0.08)

        elif pattern == PATTERN_OCR_SEARCHING:
            self.vibrate_both(0.08)
            time.sleep(0.08)
            self.vibrate_both(0.08)

        elif pattern == PATTERN_ARRIVED:
            for _ in range(2):
                self.vibrate_both(0.4)
                time.sleep(0.2)

        elif pattern == PATTERN_NETWORK_ERROR:
            self.vibrate_left(0.1)
            time.sleep(0.1)
            self.vibrate_right(0.1)
            time.sleep(0.1)
            self.vibrate_left(0.1)
            time.sleep(0.1)
            self.vibrate_right(0.1)

        elif pattern == PATTERN_ERROR:
            for _ in range(4):
                self.vibrate_both(0.08)
                time.sleep(0.08)

        else:
            self.stop_all()

    def cleanup(self):
        if self.is_setup:
            self.stop_all()
            GPIO.cleanup()
            self.is_setup = False