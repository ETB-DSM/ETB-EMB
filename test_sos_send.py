"""SOS API 실제 전송 테스트 파일.

낙상 감지 없이 테스트용 SOS payload를 만들어 백엔드 /api/sos로 전송한다.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from config import DEVICE_ID, USER_ID
from network.api_client import send_sos


KST = timezone(timedelta(hours=9))


def now_kst_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def main():
    payload = {
        "userId": USER_ID,
        "deviceId": DEVICE_ID,
        "eventType": "fall_detected",
        "latitude": 36.3504,
        "longitude": 127.3845,
        "battery": 80,
        "timestamp": now_kst_iso(),
    }

    print("sos send test started")
    print("request:")
    print(payload)

    response = send_sos(
        user_id=payload["userId"],
        device_id=payload["deviceId"],
        event_type=payload["eventType"],
        latitude=payload["latitude"],
        longitude=payload["longitude"],
        battery=payload["battery"],
        timestamp=payload["timestamp"],
    )

    print("response:")
    print(response)


if __name__ == "__main__":
    main()
