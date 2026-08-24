"""MPU6050 기반 낙상 감지 테스트 실행 파일.

IMU 값을 계속 읽으면서 낙상 의심/감지 상태를 출력한다.
--vibrate 옵션을 주면 낙상 감지 시 진동모터 패턴도 함께 실행한다.
"""

from argparse import ArgumentParser
from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from sensors.imu import MPU6050
from safety.fall_detection import FallDetector

try:
    from actuators.vibration import PATTERN_ERROR, VibrationMotorController
    from config import LEFT_VIBRATION_PIN, RIGHT_VIBRATION_PIN
except ImportError:
    PATTERN_ERROR = None
    VibrationMotorController = None
    LEFT_VIBRATION_PIN = None
    RIGHT_VIBRATION_PIN = None


def main():
    parser = ArgumentParser()
    parser.add_argument("--bus", type=int, default=2)
    parser.add_argument("--address", type=lambda value: int(value, 0), default=0x68)
    parser.add_argument("--vibrate", action="store_true")
    parser.add_argument("--cooldown", type=float, default=5.0)
    args = parser.parse_args()

    imu = MPU6050(bus_number=args.bus, address=args.address)
    detector = FallDetector(fall_hold_time_sec=0.5)

    vibration = None
    last_vibration_at = 0.0

    try:
        imu.connect()

        if args.vibrate:
            if VibrationMotorController is None:
                raise RuntimeError("vibration module is not available")

            vibration = VibrationMotorController(
                left_pin=LEFT_VIBRATION_PIN,
                right_pin=RIGHT_VIBRATION_PIN,
            )
            vibration.setup()

        print("fall detection test started")
        print(f"imu bus={args.bus}, address={hex(args.address)}")
        print("press Ctrl+C to stop")

        while True:
            imu_data = imu.read_all()
            result = detector.update(imu_data)

            print(
                f"status={result['status']} "
                f"fall={result['fall_detected']} "
                f"accel_mag={result['accel_magnitude']:.2f}g "
                f"impact={result['impact']} "
                f"free_fall={result['free_fall']} "
                f"tilt={result['unstable_tilt']} "
                f"pitch={result['pitch']:.1f} "
                f"roll={result['roll']:.1f}"
            )

            if result["fall_detected"] and vibration is not None:
                now = time.time()

                if now - last_vibration_at >= args.cooldown:
                    vibration.play_pattern(PATTERN_ERROR)
                    last_vibration_at = now

            time.sleep(0.2)

    finally:
        if vibration is not None:
            vibration.force_stop_all()
            vibration.cleanup()

        imu.close()


if __name__ == "__main__":
    main()