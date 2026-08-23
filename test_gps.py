"""NEO-M8N GPS 단독 테스트 실행 파일."""

from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from sensors.gps import GpsReader
from config import GPS_PORT, GPS_BAUDRATE


def main():
    gps = GpsReader(port=GPS_PORT, baudrate=GPS_BAUDRATE)

    try:
        gps.connect()

        print("gps test started")
        print(f"port={GPS_PORT}, baudrate={GPS_BAUDRATE}")
        print("press Ctrl+C to stop")

        while True:
            location = gps.read_location()

            if location is None:
                print("gps: no valid location")
            else:
                print(location)

            time.sleep(1)

    finally:
        gps.close()


if __name__ == "__main__":
    main()