"""낙상 감지 시 SOS 요청 데이터 생성 테스트 파일.

IMU로 낙상을 감지하면 GPS 위치를 읽고, 백엔드 SOS API에 보낼 JSON payload를 만든다.
이 파일은 아직 서버로 전송하지 않고 콘솔에 출력만 한다.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import sys
import time

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from sensors.imu import MPU6050
from sensors.gps import GpsReader
from safety.fall_detection import FallDetector
from config import GPS_PORT, GPS_BAUDRATE


USER_ID = "user_001"
DEVICE_ID = "aicane_001"
DEFAULT_BATTERY = 80

KST = timezone(timedelta(hours=9))


def now_kst_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def read_current_location(gps, max_attempts: int = 5):
    for _ in range(max_attempts):
        location = gps.read_location()

        if location and location.get("valid"):
            return {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
            }

        time.sleep(0.5)

    return {
        "latitude": None,
        "longitude": None,
    }


def make_sos_payload(event_type, location, battery):
    return {
        "userId": USER_ID,
        "deviceId": DEVICE_ID,
        "eventType": event_type,
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "battery": battery,
        "timestamp": now_kst_iso(),
    }


def main():
    imu = MPU6050(bus_number=2, address=0x68)
    gps = GpsReader(port=GPS_PORT, baudrate=GPS_BAUDRATE)
    detector = FallDetector(fall_hold_time_sec=0.5)

    try:
        imu.connect()
        gps.connect()

        print("sos payload test started")
        print("fall detected -> make SOS payload")
        print("press Ctrl+C to stop")

        while True:
            imu_data = imu.read_all()
            result = detector.update(imu_data)

            print(
                f"status={result['status']} "
                f"fall={result['fall_detected']} "
                f"accel_mag={result['accel_magnitude']:.2f}g "
                f"pitch={result['pitch']:.1f} "
                f"roll={result['roll']:.1f}"
            )

            if result["fall_detected"]:
                location = read_current_location(gps)
                payload = make_sos_payload(
                    event_type="fall_detected",
                    location=location,
                    battery=DEFAULT_BATTERY,
                )

                print("SOS PAYLOAD")
                print(json.dumps(payload, ensure_ascii=False, indent=2))

                time.sleep(5)
                detector.reset()

            time.sleep(0.2)

    finally:
        imu.close()
        gps.close()


if __name__ == "__main__":
    main()