"""MPU6050 IMU 단독 테스트 실행 파일."""

from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from sensors.imu import MPU6050
from config import IMU_BUS_NUMBER, IMU_ADDRESS


def main():
    imu = MPU6050(
        bus_number=IMU_BUS_NUMBER,
        address=IMU_ADDRESS,
    )

    try:
        imu.connect()

        print("imu test started")
        print(f"bus={IMU_BUS_NUMBER}, address={hex(IMU_ADDRESS)}")
        print("press Ctrl+C to stop")

        while True:
            data = imu.read_all()

            accel = data["accel"]
            gyro = data["gyro"]
            tilt = data["tilt"]

            print(
                f"accel=({accel['x']:.2f}, {accel['y']:.2f}, {accel['z']:.2f}) "
                f"gyro=({gyro['x']:.1f}, {gyro['y']:.1f}, {gyro['z']:.1f}) "
                f"pitch={tilt['pitch']:.1f} "
                f"roll={tilt['roll']:.1f} "
                f"temp={data['temp']:.1f}C"
            )

            time.sleep(0.2)

    finally:
        imu.close()


if __name__ == "__main__":
    main()