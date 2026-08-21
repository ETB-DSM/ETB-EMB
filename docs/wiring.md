# AI-Cane Embedded Wiring Guide

이 문서는 AI-Cane 임베디드 파트의 실제 배선 기준을 정리한 문서이다.  
Orange Pi 5 Plus에 센서, 모터, 카메라를 연결할 때 이 문서를 기준으로 배선한다.

---

## 1. 전체 구조

```text
Orange Pi 5 Plus
├─ I2C2_M0: MPU6050 + TCA9548A
│  └─ TCA9548A: TF-Luna LiDAR 여러 개 연결
├─ UART6_M1: GPS
├─ UART3_M1: TF-Luna LiDAR 1개 단품 테스트
├─ USB: USB 카메라
└─ GPIO: 진동모터 제어 신호
```

---

## 2. Orange Pi 기본 전원 / GND 핀

| 용도 | 40핀 번호 | 설명 |
|---|---:|---|
| 3.3V | 1, 17 | I2C 모듈 로직 전원용 |
| 5V | 2, 4 | 센서/모듈 전원용 |
| GND | 6, 9, 14, 20, 25, 30, 34, 39 | 모든 모듈 GND 공통 연결 |

### 주의사항

- 모든 센서와 모터 모듈의 GND는 Orange Pi GND와 반드시 공통으로 연결한다.
- 모터 전원은 GPIO 핀에서 직접 공급하지 않는다.
- 5V 핀 사용 시 전체 전류 소모를 확인한다.
- Orange Pi GPIO 로직은 3.3V 기준이다.

---

## 3. I2C 배선: MPU6050 + TCA9548A

Orange Pi의 I2C2_M0 라인에 MPU6050과 TCA9548A를 함께 연결한다.

| 기능 | Orange Pi 40핀 | 장치 연결 |
|---|---:|---|
| SDA | Pin 3 | MPU6050 SDA, TCA9548A SDA |
| SCL | Pin 5 | MPU6050 SCL, TCA9548A SCL |
| 3.3V | Pin 1 또는 17 | MPU6050 VCC, TCA9548A VCC |
| GND | GND 핀 | MPU6050 GND, TCA9548A GND |

### 확인 명령

```bash
ls /dev/i2c-*
sudo i2cdetect -y 2
```

### 예상 확인값

| 장치 | 예상 주소 |
|---|---|
| MPU6050 | 0x68 또는 0x69 |
| TCA9548A | 0x70 |

### 주의사항

- I2C 모듈 VCC는 우선 3.3V 사용을 기준으로 한다.
- 모듈별 전원 허용 전압은 실제 부품 스펙을 확인한다.
- I2C 장치가 보이지 않으면 SDA/SCL 반대 연결, GND 미공통, 인터페이스 비활성화를 먼저 확인한다.

---

## 4. TF-Luna 여러 개 배선: TCA9548A 사용

TF-Luna를 여러 개 사용할 경우 I2C 주소 충돌을 피하기 위해 TCA9548A I2C 멀티플렉서를 사용한다.

| TF-Luna 위치 | TCA9548A 채널 | 연결 |
|---|---:|---|
| 전방 LiDAR | CH0 | SDA0 / SCL0 |
| 좌측 LiDAR | CH1 | SDA1 / SCL1 |
| 우측 LiDAR | CH2 | SDA2 / SCL2 |
| 상단 LiDAR | CH3 | SDA3 / SCL3 |
| 예비 LiDAR | CH4 | SDA4 / SCL4 |

### TF-Luna I2C 모드 기준 배선

| TF-Luna 핀 | 연결 |
|---|---|
| VCC | 5V |
| GND | GND |
| SDA | TCA9548A 해당 채널 SDA |
| SCL | TCA9548A 해당 채널 SCL |
| Mode Select | TF-Luna 매뉴얼 기준 I2C 모드 설정 |
| 기타 핀 | 사용하지 않으면 미연결 |

### 주의사항

- TF-Luna 케이블 색상은 믿지 말고 핀 번호 기준으로 연결한다.
- TF-Luna 기본 통신 모드가 UART일 수 있으므로 I2C 모드 설정 여부를 반드시 확인한다.
- 여러 개 연결 전에는 TF-Luna 1개를 UART로 먼저 단품 테스트한다.

---

## 5. TF-Luna 1개 단품 테스트용 UART 배선

처음에는 여러 개를 바로 연결하지 않고 UART로 TF-Luna 1개만 테스트한다.

| 기능 | Orange Pi 40핀 | TF-Luna 연결 |
|---|---:|---|
| UART3 TX | Pin 16 | TF-Luna RXD |
| UART3 RX | Pin 18 | TF-Luna TXD |
| 5V | Pin 2 또는 4 | TF-Luna VCC |
| GND | GND 핀 | TF-Luna GND |

### 연결 기준

```text
Orange Pi TX → TF-Luna RXD
Orange Pi RX → TF-Luna TXD
GND → GND 공통
```

### 예상 장치명

```bash
/dev/ttyS3
```

### 확인 명령

```bash
ls /dev/ttyS*
```

### LiDAR 테스트 실행 예시

```bash
python src/sensors/lidar.py
```

### 정상 출력 예시

```text
distance=120cm strength=850 temp=32.1C
distance=121cm strength=848 temp=32.1C
```

---

## 6. GPS 배선: UART6_M1

GPS는 UART6_M1에 연결한다.

| 기능 | Orange Pi 40핀 | GPS 연결 |
|---|---:|---|
| UART6 TX | Pin 8 | GPS RX |
| UART6 RX | Pin 10 | GPS TX |
| 5V 또는 3.3V | 모듈 스펙 확인 | GPS VCC |
| GND | GND 핀 | GPS GND |

### 주의사항

- GPS VCC는 사용하는 GPS 모듈 스펙을 확인한 뒤 5V 또는 3.3V를 선택한다.
- TX/RX는 서로 교차 연결한다.
- GPS 기본 Baudrate는 보통 9600bps이다.

### 예상 장치명

```bash
/dev/ttyS6
```

### 확인 명령

```bash
ls /dev/ttyS*
```

---

## 7. 진동모터 배선

YwRobot 진동모터 모듈은 GPIO가 모터 전원을 직접 공급하는 방식이 아니라 제어 신호만 주는 방식으로 사용한다.

| 모터 위치 | Orange Pi GPIO 핀 | 모터 모듈 연결 |
|---|---:|---|
| 전방 진동 | Pin 11 | SIG |
| 좌측 진동 | Pin 13 | SIG |
| 우측 진동 | Pin 15 | SIG |
| 공통 전원 | 5V 분배선 | VCC |
| 공통 GND | GND | GND |

### 주의사항

- GPIO는 SIG 제어 신호만 연결한다.
- 모터 VCC를 GPIO 핀에서 직접 공급하지 않는다.
- 모터 전원은 가능하면 별도 5V 분배선을 사용한다.
- Orange Pi GND와 모터 GND는 반드시 공통으로 연결한다.
- 모터 여러 개를 동시에 켤 경우 전류 부족 여부를 확인한다.

---

## 8. 서보모터 배선

서보모터는 PWM 제어 신호와 별도 5V 전원이 필요하다.

| 기능 | Orange Pi 연결 | 서보모터 연결 |
|---|---|---|
| PWM 또는 GPIO 신호 | 사용할 GPIO 핀 확정 필요 | Signal |
| 5V | 별도 5V 전원 또는 5V 분배선 | VCC |
| GND | Orange Pi GND와 공통 | GND |

### 주의사항

- 서보모터 VCC를 Orange Pi GPIO 핀에서 직접 공급하지 않는다.
- 서보모터는 순간 전류가 커질 수 있으므로 전원 안정성을 확인한다.
- Orange Pi GND와 서보모터 GND는 반드시 공통으로 연결한다.
- PWM 가능 핀은 Orange Pi 설정과 실제 핀맵 확인 후 확정한다.

---

## 9. USB 카메라 배선

| 부품 | 연결 |
|---|---|
| USB 카메라 | Orange Pi USB 포트 |

### 확인 명령

```bash
ls /dev/video*
```

### OpenCV 테스트 예시

```bash
python src/sensors/camera.py
```

---

## 10. 활성화해야 할 Orange Pi 인터페이스

`orangepi-config`에서 Hardware 설정으로 활성화하거나 `/boot/extlinux/extlinux.conf`에 overlay를 추가한다.

### 필요 인터페이스

```text
i2c2-m0
uart6-m1
uart3-m1
```

### 확인 명령

```bash
ls /dev/i2c-*
ls /dev/ttyS*
gpio readall
```

---

## 11. 개발 및 배선 테스트 순서

1. Orange Pi 전원 안정성 확인
2. I2C2_M0 활성화
3. MPU6050만 연결해서 `i2cdetect` 확인
4. TCA9548A만 연결해서 `0x70` 확인
5. UART3로 TF-Luna 1개 거리값 테스트
6. UART6로 GPS NMEA 데이터 확인
7. 진동모터 1개 GPIO 제어 테스트
8. LiDAR + 장애물 판단 + 진동모터 통합
9. 서보모터 단독 제어 테스트
10. LiDAR + 서보모터 통합
11. TCA9548A에 TF-Luna 여러 개 연결
12. USB 카메라 연결 확인
13. OCR / YOLO 기능 연결
14. Backend API 연동
15. 전체 통합 시연 테스트

---

## 12. 최종 배선 결론

```text
Orange Pi 5 Plus 한 개로 전체 제어 가능하다.

LiDAR 여러 개 → TCA9548A 사용
TF-Luna 1개 테스트 → UART3 사용
GPS → UART6 사용
MPU6050 → I2C 사용
USB 카메라 → USB 포트 사용
진동모터 → GPIO 제어 신호 + 별도 5V 전원
서보모터 → PWM/GPIO 제어 신호 + 별도 5V 전원

모든 모듈의 GND는 반드시 Orange Pi GND와 공통 연결한다.
```
