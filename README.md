# AI-Cane Embedded

AI-Cane 임베디드 파트 코드 저장소이다.  
Orange Pi 5 Plus에서 센서 데이터를 읽고, 장애물 판단과 진동 피드백을 수행한다.

## 실행 환경

- Board: Orange Pi 5 Plus
- Language: Python
- OS: Ubuntu Linux
- Main Devices:
  - TF-Luna LiDAR
  - TCA9548A I2C Multiplexer
  - YwRobot Vibration Motor Module
  - MPU6050 IMU
  - GPS Module
  - USB Camera

## 폴더 구조

```text
embedded/
├─ src/
│  ├─ sensors/       # LiDAR, GPS, IMU, Camera 입력 코드
│  ├─ actuators/     # Vibration, Servo 출력 코드
│  ├─ ai/            # YOLO, OCR 분석 코드
│  ├─ network/       # Backend API 통신 코드
│  ├─ navigation/    # 목적지 판단 코드
│  ├─ utils/         # 공통 유틸리티
│  ├─ config.py      # 공통 설정값
│  ├─ obstacle_logic.py
│  └─ main.py        # 최종 통합 실행 파일
├─ docs/
│  ├─ wiring.md
│  ├─ bringup_checklist.md
│  └─ sensor_test_plan.md
├─ tests/
└─ requirements.txt
```

## 개발 원칙

각 파일은 자기 역할만 담당한다.

```text
camera.py    → 카메라 frame 반환
yolo.py      → frame에서 객체 탐지
ocr.py       → frame에서 글자 인식
lidar.py     → 거리값 반환
vibration.py → 진동모터 제어
main.py      → 전체 기능 통합
```

## 설치

```bash
pip install -r requirements.txt
```

## 현재 개발 순서

1. Orange Pi 부팅 및 전원 안정화
2. TF-Luna LiDAR 1개 UART 테스트
3. LiDAR 5개 I2C/TCA9548A 구조 확인
4. 장애물 판단 로직 확인
5. 진동모터 단독 제어
6. LiDAR + 진동 통합
7. 카메라 frame 수신
8. YOLO/OCR 연동
9. GPS/Backend 연동
10. main.py 최종 통합

## 팀원 코드 통합 기준

팀원 코드는 바로 `main.py`에 붙이지 않는다.  
먼저 담당 파일에 넣고, 함수 이름과 반환 형식이 맞는지 확인한 뒤 마지막에 `main.py`에서 연결한다.

| 담당 | 파일 | 필수 반환/동작 |
|---|---|---|
| LiDAR | `src/sensors/lidar.py` | 거리값 cm 또는 방향별 거리 dict 반환 |
| 진동모터 | `src/actuators/vibration.py` | 장애물 상태를 받아 진동모터 제어 |
| 서보모터 | `src/actuators/servo.py` | 각도 입력을 받아 서보 위치 제어 |
| 카메라 | `src/sensors/camera.py` | OpenCV frame 반환 |
| YOLO | `src/ai/yolo.py` | 객체 탐지 결과 list 반환 |
| OCR | `src/ai/ocr.py` | 텍스트 인식 결과 dict 반환 |
| GPS | `src/sensors/gps.py` | 현재 위치 dict 반환 |
