"""IMU 데이터를 기반으로 낙상 가능성을 판단하는 파일.

MPU6050에서 읽은 accel, gyro, tilt 값을 받아서 지팡이가 강하게 떨어졌거나
비정상적으로 누운 상태가 유지되는지 판단한다.
"""

import math
import time


FALL_STATUS_NORMAL = "normal"
FALL_STATUS_SUSPECTED = "suspected"
FALL_STATUS_DETECTED = "detected"

FREE_FALL_THRESHOLD_G = 0.45
IMPACT_THRESHOLD_G = 2.2
TILT_THRESHOLD_DEG = 65.0
FALL_HOLD_TIME_SEC = 1.0


def calculate_accel_magnitude(accel):
    x = accel["x"]
    y = accel["y"]
    z = accel["z"]

    return math.sqrt(x * x + y * y + z * z)


def is_free_fall(accel_magnitude):
    return accel_magnitude <= FREE_FALL_THRESHOLD_G


def is_impact(accel_magnitude):
    return accel_magnitude >= IMPACT_THRESHOLD_G


def is_unstable_tilt(tilt):
    pitch = abs(tilt["pitch"])
    roll = abs(tilt["roll"])

    return pitch >= TILT_THRESHOLD_DEG or roll >= TILT_THRESHOLD_DEG


class FallDetector:
    def __init__(
        self,
        fall_hold_time_sec: float = FALL_HOLD_TIME_SEC,
    ):
        self.fall_hold_time_sec = fall_hold_time_sec
        self.suspected_started_at = None
        self.last_status = FALL_STATUS_NORMAL

    def reset(self):
        self.suspected_started_at = None
        self.last_status = FALL_STATUS_NORMAL

    def update(self, imu_data, timestamp: float | None = None):
        if timestamp is None:
            timestamp = time.time()

        accel = imu_data["accel"]
        gyro = imu_data["gyro"]
        tilt = imu_data["tilt"]

        accel_magnitude = calculate_accel_magnitude(accel)
        free_fall = is_free_fall(accel_magnitude)
        impact = is_impact(accel_magnitude)
        unstable_tilt = is_unstable_tilt(tilt)

        fall_suspected = free_fall or impact or unstable_tilt

        if fall_suspected:
            if self.suspected_started_at is None:
                self.suspected_started_at = timestamp

            suspected_duration = timestamp - self.suspected_started_at

            if suspected_duration >= self.fall_hold_time_sec:
                self.last_status = FALL_STATUS_DETECTED
            else:
                self.last_status = FALL_STATUS_SUSPECTED

        else:
            self.reset()
            suspected_duration = 0.0

        return {
            "fall_detected": self.last_status == FALL_STATUS_DETECTED,
            "status": self.last_status,
            "accel_magnitude": accel_magnitude,
            "free_fall": free_fall,
            "impact": impact,
            "unstable_tilt": unstable_tilt,
            "suspected_duration": suspected_duration,
            "pitch": tilt["pitch"],
            "roll": tilt["roll"],
            "gyro": gyro,
        }