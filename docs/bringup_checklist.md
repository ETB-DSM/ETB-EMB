# AI-Cane Bring-up Checklist

부품을 한 번에 전부 연결하지 않고, 아래 순서대로 하나씩 확인한다.

## 1. Orange Pi 기본 확인

- [ ] 안정적인 전원 연결
- [ ] OS 부팅 확인
- [ ] 인터넷 연결 확인
- [ ] SSH 또는 원격 접속 확인
- [ ] Python 버전 확인
- [ ] `requirements.txt` 설치 확인

```bash
python --version
pip install -r requirements.txt
```

## 2. 인터페이스 확인

- [ ] I2C 활성화
- [ ] UART 활성화
- [ ] USB 카메라 인식 확인
- [ ] GPIO 제어 가능 여부 확인

```bash
ls /dev/i2c-*
ls /dev/ttyS*
ls /dev/video*
```

## 3. LiDAR 확인

- [ ] TF-Luna 1개 UART 연결
- [ ] `/dev/ttyS3` 확인
- [ ] 거리값 출력 확인
- [ ] TCA9548A 연결
- [ ] I2C 주소 `0x70` 확인
- [ ] TF-Luna I2C 모드 확인
- [ ] LiDAR 5개 거리값 dict 반환 확인

## 4. 진동모터 확인

- [ ] VCC / GND / IN 배선 확인
- [ ] Orange Pi GND와 모터 GND 공통 연결
- [ ] 왼쪽 진동모터 ON/OFF 확인
- [ ] 오른쪽 진동모터 ON/OFF 확인
- [ ] weak / medium / strong 패턴 확인

## 5. 서보모터 확인

- [ ] VCC / GND / Signal 배선 확인
- [ ] Orange Pi GND와 서보모터 GND 공통 연결
- [ ] 0도 / 90도 / 180도 이동 확인
- [ ] 설정 각도와 실제 움직임 방향 확인

## 6. 카메라 확인

- [ ] USB 카메라 연결
- [ ] `/dev/video0` 확인
- [ ] frame 수신 확인
- [ ] frame 저장 없이 메모리에서 처리 확인

## 7. AI 확인

- [ ] YOLO 모델 로드 확인
- [ ] 객체 탐지 결과 반환 확인
- [ ] OCR 모델 로드 확인
- [ ] 텍스트 인식 결과 반환 확인

## 8. GPS 확인

- [ ] GPS 전원 연결 확인
- [ ] UART 포트 확인
- [ ] NMEA 데이터 수신 확인
- [ ] 위도/경도 반환 확인

## 9. Backend API 확인

- [ ] 서버 주소 설정 확인
- [ ] 장치 상태 전송 확인
- [ ] SOS 이벤트 전송 확인
- [ ] 네트워크 실패 시 예외 처리 확인

## 10. 통합 확인

- [ ] LiDAR 거리값 수신
- [ ] 장애물 위험도 판단
- [ ] 진동 명령 생성
- [ ] 진동모터 동작
- [ ] 카메라 frame 수신
- [ ] YOLO/OCR 결과 수신
- [ ] GPS 위치 수신
- [ ] Backend API 전송
- [ ] main.py 통합 실행