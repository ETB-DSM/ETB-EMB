"""GPS 모듈에서 현재 위치를 읽는 파일.

UART 또는 USB 시리얼로 들어오는 GPS 데이터를 읽고, 위도/경도 같은 위치 정보로
변환하는 역할을 담당한다.
"""

import serial

from config import GPS_BAUDRATE, GPS_PORT, GPS_TIMEOUT_SEC


def convert_nmea_to_decimal(raw_value, direction):
    """NMEA 좌표 형식을 일반 위도/경도 decimal 형식으로 변환한다.

    NMEA 예:
    - 위도: 3723.2475,N
    - 경도: 12703.1234,E

    반환 예:
    - 37.387458
    - 127.052056
    """
    if not raw_value:
        return None

    if not direction:
        return None

    if direction in ["N", "S"]:
        degree_length = 2
    elif direction in ["E", "W"]:
        degree_length = 3
    else:
        return None

    try:
        degrees = float(raw_value[:degree_length])
        minutes = float(raw_value[degree_length:])
    except ValueError:
        return None

    decimal = degrees + minutes / 60

    if direction in ["S", "W"]:
        decimal *= -1

    return decimal


class GpsReader:
    """NEO-M8N GPS UART 데이터를 읽고 위치 dict를 반환하는 클래스."""

    def __init__(
        self,
        port=GPS_PORT,
        baudrate=GPS_BAUDRATE,
        timeout=GPS_TIMEOUT_SEC,
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def connect(self):
        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
        )

        self.serial.reset_input_buffer()

    def close(self):
        if self.serial is not None and self.serial.is_open:
            self.serial.close()

    def read_line(self):
        if self.serial is None:
            raise RuntimeError("GPS serial is not connected")

        line = self.serial.readline()

        if not line:
            return None

        return line.decode("ascii", errors="ignore").strip()

    def parse_gga(self, sentence):
        """GGA 문장에서 위치 정보를 추출한다."""
        parts = sentence.split(",")

        if len(parts) < 7:
            return None

        fix_quality = parts[6]

        if fix_quality == "0":
            return {
                "latitude": None,
                "longitude": None,
                "valid": False,
                "source": "GGA",
            }

        latitude = convert_nmea_to_decimal(parts[2], parts[3])
        longitude = convert_nmea_to_decimal(parts[4], parts[5])

        if latitude is None or longitude is None:
            return None

        return {
            "latitude": latitude,
            "longitude": longitude,
            "valid": True,
            "source": "GGA",
        }

    def parse_rmc(self, sentence):
        """RMC 문장에서 위치 정보를 추출한다."""
        parts = sentence.split(",")

        if len(parts) < 7:
            return None

        status = parts[2]

        if status != "A":
            return {
                "latitude": None,
                "longitude": None,
                "valid": False,
                "source": "RMC",
            }

        latitude = convert_nmea_to_decimal(parts[3], parts[4])
        longitude = convert_nmea_to_decimal(parts[5], parts[6])

        if latitude is None or longitude is None:
            return None

        return {
            "latitude": latitude,
            "longitude": longitude,
            "valid": True,
            "source": "RMC",
        }

    def parse_sentence(self, sentence):
        """NMEA 문장 종류에 맞는 파싱 함수를 호출한다."""
        if sentence.startswith("$GPGGA") or sentence.startswith("$GNGGA"):
            return self.parse_gga(sentence)

        if sentence.startswith("$GPRMC") or sentence.startswith("$GNRMC"):
            return self.parse_rmc(sentence)

        return None

    def read_location(self, max_attempts=30):
        """GPS 위치 정보를 읽는다.

        max_attempts 횟수만큼 NMEA 문장을 읽고, 위치 정보가 있는 문장을 찾는다.
        위치를 못 찾으면 valid=False 상태를 반환한다.
        """
        for _ in range(max_attempts):
            sentence = self.read_line()

            if sentence is None:
                continue

            location = self.parse_sentence(sentence)

            if location is None:
                continue

            return location

        return {
            "latitude": None,
            "longitude": None,
            "valid": False,
            "source": None,
        }

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()