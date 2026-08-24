"""TF-Luna LiDAR 1개 I2C 거리 측정 테스트 파일."""

from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from smbus2 import SMBus


BUS_NUMBER = 2
ADDRESS = 0x10


def read_lidar(bus):
    data = bus.read_i2c_block_data(ADDRESS, 0x00, 6)

    distance_cm = data[0] + data[1] * 256
    strength = data[2] + data[3] * 256
    temperature = (data[4] + data[5] * 256) / 100

    return {
        "distance_cm": distance_cm,
        "strength": strength,
        "temperature": temperature,
    }


def main():
    bus = SMBus(BUS_NUMBER)

    try:
        print("TF-Luna I2C test started")
        print(f"bus=/dev/i2c-{BUS_NUMBER}, address=0x{ADDRESS:02X}")
        print("press Ctrl+C to stop")

        while True:
            try:
                data = read_lidar(bus)
                print(
                    f"distance={data['distance_cm']}cm "
                    f"strength={data['strength']} "
                    f"temp={data['temperature']:.1f}C"
                )
            except OSError as error:
                print(f"i2c read error: {error}")

            time.sleep(0.1)

    finally:
        bus.close()


if __name__ == "__main__":
    main()