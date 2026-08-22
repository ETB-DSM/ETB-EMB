"""진동모터 active-high 방식 단독 테스트 파일.

이 파일은 기존 vibration.py를 사용하지 않고 sysfs GPIO를 직접 제어한다.

가정:
- GPIO 값 1 = 진동 ON
- GPIO 값 0 = 진동 OFF

현재 연결 후보:
- 왼쪽 진동모터: GPIO36, 물리 Pin 11
- 오른쪽 진동모터: GPIO39, 물리 Pin 13
"""

from argparse import ArgumentParser
import time
from pathlib import Path


GPIO_PATH = Path("/sys/class/gpio")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


class GpioOutput:
    def __init__(self, gpio_number: int):
        self.gpio_number = gpio_number
        self.path = GPIO_PATH / f"gpio{gpio_number}"

    def setup(self):
        if not self.path.exists():
            write_text(GPIO_PATH / "export", str(self.gpio_number))
            time.sleep(0.1)

        write_text(self.path / "direction", "out")
        self.off()

    def on(self):
        write_text(self.path / "value", "1")

    def off(self):
        write_text(self.path / "value", "0")

    def read_value(self) -> str:
        return (self.path / "value").read_text().strip()

    def cleanup(self):
        self.off()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--pin", type=int, required=True)
    parser.add_argument("--duration", type=float, default=1.0)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()

    motor = GpioOutput(args.pin)

    try:
        motor.setup()

        print("active-high vibration test started")
        print(f"gpio={args.pin}")
        print("OFF=0, ON=1")

        print("force off")
        motor.off()
        print(f"value={motor.read_value()}")
        time.sleep(1)

        for index in range(args.repeat):
            print(f"on {index + 1}")
            motor.on()
            print(f"value={motor.read_value()}")
            time.sleep(args.duration)

            print(f"off {index + 1}")
            motor.off()
            print(f"value={motor.read_value()}")
            time.sleep(1)

        print("active-high vibration test finished")

    finally:
        motor.cleanup()
        print("cleanup off")


if __name__ == "__main__":
    main()