"""진동모터 제어 파일.

YwRobot 진동모터 모듈 2개를 제어한다.

길안내, 장애물 경고, 목적지 도착, 시스템 오류를 서로 다른 진동 패턴으로
구분해서 출력한다.

이 파일은 장애물 여부나 도착 여부를 판단하지 않는다.
요청받은 진동 패턴을 실제 모터로 출력하는 역할만 담당한다.
"""

import time

import OPi.GPIO as GPIO


LEFT_MOTOR = "left"
RIGHT_MOTOR = "right"
BOTH_MOTORS = "both"

PATTERN_STRAIGHT = "straight"
PATTERN_PREPARE_LEFT = "prepare_left"
PATTERN_PREPARE_RIGHT = "prepare_right"
PATTERN_LEFT = "left"
PATTERN_RIGHT = "right"
PATTERN_FRONT_OBSTACLE = "front_obstacle"
PATTERN_LEFT_OBSTACLE = "left_obstacle"
PATTERN_RIGHT_OBSTACLE = "right_obstacle"
PATTERN_ARRIVED = "arrived"
PATTERN_OCR_SEARCHING = "ocr_searching"
PATTERN_ERROR = "error"
PATTERN_NETWORK_ERROR = "network_error"


class VibrationMotorController:
    def __init__(self, left_pin: int, right_pin: int):
        self.left_pin = left_pin
        self.right_pin = right_pin
        self.is_setup = False

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        GPIO.setup(self.left_pin, GPIO.OUT)
        GPIO.setup(self.right_pin, GPIO.OUT)

        GPIO.output(self.left_pin, GPIO.LOW)
        GPIO.output(self.right_pin, GPIO.LOW)

        self.is_setup = True

    def _check_setup(self):
        if not self.is_setup:
            raise RuntimeError("vibration motor controller is not set up")

    def _set_motor(self, motor, state):
        self._check_setup()

        if motor == LEFT_MOTOR:
            GPIO.output(self.left_pin, GPIO.HIGH if state else GPIO.LOW)

        elif motor == RIGHT_MOTOR:
            GPIO.output(self.right_pin, GPIO.HIGH if state else GPIO.LOW)

        elif motor == BOTH_MOTORS:
            GPIO.output(self.left_pin, GPIO.HIGH if state else GPIO.LOW)
            GPIO.output(self.right_pin, GPIO.HIGH if state else GPIO.LOW)

        else:
            raise ValueError(f"unknown motor: {motor}")

    def stop_all(self):
        self._check_setup()
        GPIO.output(self.left_pin, GPIO.LOW)
        GPIO.output(self.right_pin, GPIO.LOW)

    def pulse(self, motor, on_time=0.2, off_time=0.2, repeat=1):
        self._check_setup()

        for _ in range(repeat):
            self._set_motor(motor, True)
            time.sleep(on_time)

            self._set_motor(motor, False)
            time.sleep(off_time)

    def play_straight(self):
        # 직진 안내: 약하게 한 번 울려 현재 방향 유지를 알려준다.
        self.pulse(BOTH_MOTORS, on_time=0.12, off_time=0.1, repeat=1)

    def play_prepare_left(self):
        # 좌회전 준비: 왼쪽을 짧게 울려 곧 좌회전임을 알려준다.
        self.pulse(LEFT_MOTOR, on_time=0.18, off_time=0.12, repeat=1)

    def play_prepare_right(self):
        # 우회전 준비: 오른쪽을 짧게 울려 곧 우회전임을 알려준다.
        self.pulse(RIGHT_MOTOR, on_time=0.18, off_time=0.12, repeat=1)

    def play_left_turn(self):
        # 지금 좌회전: 왼쪽을 길게 반복해서 즉시 좌회전임을 알려준다.
        self.pulse(LEFT_MOTOR, on_time=0.45, off_time=0.25, repeat=2)

    def play_right_turn(self):
        # 지금 우회전: 오른쪽을 길게 반복해서 즉시 우회전임을 알려준다.
        self.pulse(RIGHT_MOTOR, on_time=0.45, off_time=0.25, repeat=2)

    def play_front_obstacle(self):
        # 정면 장애물: 양쪽을 빠르게 반복해서 즉시 주의가 필요함을 알려준다.
        self.pulse(BOTH_MOTORS, on_time=0.08, off_time=0.08, repeat=5)

    def play_left_obstacle(self):
        # 왼쪽 장애물: 왼쪽을 빠르게 반복해서 왼쪽 장애물을 알려준다.
        self.pulse(LEFT_MOTOR, on_time=0.08, off_time=0.08, repeat=5)

    def play_right_obstacle(self):
        # 오른쪽 장애물: 오른쪽을 빠르게 반복해서 오른쪽 장애물을 알려준다.
        self.pulse(RIGHT_MOTOR, on_time=0.08, off_time=0.08, repeat=5)

    def play_arrived(self):
        # 도착: 양쪽을 길게 반복해서 목적지 도착을 알려준다.
        self.pulse(BOTH_MOTORS, on_time=0.5, off_time=0.3, repeat=3)

    def play_ocr_searching(self):
        # 목적지 근처 OCR 확인 중임을 양쪽 진동으로 알려준다.
        self.pulse(BOTH_MOTORS, on_time=0.15, off_time=0.4, repeat=2)

    def play_error(self):
        # 일반 장치 오류를 양쪽 짧은 진동으로 알려준다.
        self.pulse(BOTH_MOTORS, on_time=0.1, off_time=0.1, repeat=3)

    def play_network_error(self):
        # 네트워크 문제를 조금 느린 3회 진동으로 알려준다.
        self.pulse(BOTH_MOTORS, on_time=0.12, off_time=0.25, repeat=3)

    def play_pattern(self, pattern):
        if pattern == PATTERN_STRAIGHT:
            self.play_straight()

        elif pattern == PATTERN_PREPARE_LEFT:
            self.play_prepare_left()

        elif pattern == PATTERN_PREPARE_RIGHT:
            self.play_prepare_right()

        elif pattern == PATTERN_LEFT:
            self.play_left_turn()

        elif pattern == PATTERN_RIGHT:
            self.play_right_turn()

        elif pattern == PATTERN_FRONT_OBSTACLE:
            self.play_front_obstacle()

        elif pattern == PATTERN_LEFT_OBSTACLE:
            self.play_left_obstacle()

        elif pattern == PATTERN_RIGHT_OBSTACLE:
            self.play_right_obstacle()

        elif pattern == PATTERN_ARRIVED:
            self.play_arrived()

        elif pattern == PATTERN_OCR_SEARCHING:
            self.play_ocr_searching()

        elif pattern == PATTERN_NETWORK_ERROR:
            self.play_network_error()

        elif pattern == PATTERN_ERROR:
            self.play_error()

        else:
            raise ValueError(f"unknown vibration pattern: {pattern}")

    def cleanup(self):
        if self.is_setup:
            self.stop_all()
            GPIO.cleanup()
            self.is_setup = False