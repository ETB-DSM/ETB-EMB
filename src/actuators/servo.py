"""서보모터 각도를 제어하는 파일.

LiDAR 또는 카메라 방향을 움직일 때 사용할 서보 제어 코드를 이 파일에 구현한다.
현재는 실제 GPIO/PWM 연결 전이라 뼈대부터 작성한다.
"""


import time
import OPi.GPIO as GPIO


class Servo:
    def __init__(self, pin: int, frequency: int = 50, min_duty: float = 2.5, max_duty: float = 12.5):
        self.pin = pin
        self.frequency = frequency
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.pwm = None
        self.current_angle = None

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)

        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)

    def _angle_to_duty(self, angle: float):
        angle = max(0, min(180, angle))
        return self.min_duty + (angle / 180.0) * (self.max_duty - self.min_duty)

    def set_angle(self, angle: float, hold_time: float = 0.3):
        if self.pwm is None:
            raise RuntimeError("servo is not set up")

        angle = max(0, min(180, angle))
        duty = self._angle_to_duty(angle)

        self.pwm.ChangeDutyCycle(duty)
        self.current_angle = angle
        time.sleep(hold_time)

        self.pwm.ChangeDutyCycle(0)

    def sweep(self, start: float, end: float, step: float = 5.0, delay: float = 0.05):
        if step <= 0:
            raise ValueError("step must be greater than 0")

        if start <= end:
            angle = start
            while angle <= end:
                self.set_angle(angle)
                time.sleep(delay)
                angle += step
        else:
            angle = start
            while angle >= end:
                self.set_angle(angle)
                time.sleep(delay)
                angle -= step

    def stop(self):
        if self.pwm is not None:
            self.pwm.stop()
            self.pwm = None