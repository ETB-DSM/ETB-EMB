"""AI-Cane 임베디드 프로그램 전체 설정 파일.

하드웨어 배선, 서버 주소, 테스트 환경에 따라 바뀔 수 있는 값을 모아둔다.
비즈니스 로직은 넣지 않고 설정값만 관리한다.
"""

# 사용자와 장치
USER_ID = "user_001"
DEVICE_ID = "aicane_001"

# 앱에서 길안내를 시작하면 서버가 발급하는 세션 ID다.
# 실제 연동 시에는 앱 또는 서버에서 받은 값으로 바꿔야 한다.
NAVIGATION_SESSION_ID = "nav_001"

# 백엔드 서버
SERVER_BASE_URL = "https://ai-cane.heijionline.com"
API_TIMEOUT_SEC = 3.0

# 메인 반복 루프
LOOP_INTERVAL_SEC = 0.3
LOCATION_UPLOAD_INTERVAL_SEC = 5.0
DEVICE_STATUS_UPLOAD_INTERVAL_SEC = 10.0

# IMU
IMU_BUS_NUMBER = 2
IMU_ADDRESS = 0x68

# GPS
GPS_PORT = "/dev/ttyS6"
GPS_BAUDRATE = 9600
GPS_TIMEOUT_SEC = 1.0

# LiDAR
LIDAR_I2C_BUS_NUMBER = 2
LIDAR_CHANNELS = {
    "front": 0,
    "left": 1,
    "right": 2,
    "upper": 3,
    "lower": 4,
}

# 카메라
CAMERA_DEVICE_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# 진동모터 GPIO BOARD 핀 번호
LEFT_VIBRATION_PIN = 36
RIGHT_VIBRATION_PIN = 39

# 목적지
DEFAULT_ARRIVAL_RADIUS_M = 30
DESTINATION_STABLE_SECONDS = 2.0

# OCR
OCR_CONFIDENCE_THRESHOLD = 0.6
OCR_RETRY_COUNT = 5
OCR_MATCH_REQUIRED_COUNT = 2

# 길안내 명령
TURN_PREPARE_DISTANCE_M = 20
TURN_NOW_DISTANCE_M = 5

# 장애물 거리 기준
DANGER_DISTANCE_CM = 50
WARNING_DISTANCE_CM = 100
NOTICE_DISTANCE_CM = 150