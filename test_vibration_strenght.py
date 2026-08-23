"""진동 세기 체감 테스트 파일."""

from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from actuators.vibration import VibrationMotorController
from config import LEFT_VIBRATION_PIN, RIGHT_VIBRATION_PIN


def main():
    vibration = VibrationMotorController(
        left_pin=LEFT_VIBRATION_PIN,
        right_pin=RIGHT_VIBRATION_PIN,
    )

    try:
        vibration.setup()

        tests = [
            ("weak", 0.2),
            ("medium", 0.5),
            ("strong", 0.9),
        ]

        for name, intensity in tests:
            print(f"left {name}: intensity={intensity}")
            vibration.vibrate_left(duration=1.5, intensity=intensity)
            time.sleep(1)

        for name, intensity in tests:
            print(f"right {name}: intensity={intensity}")
            vibration.vibrate_right(duration=1.5, intensity=intensity)
            time.sleep(1)

    finally:
        vibration.force_stop_all()
        vibration.cleanup()


if __name__ == "__main__":
    main()