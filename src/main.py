"""AI-Cane 메인 실행 루프.

센서, 백엔드 API, 길안내 로직, OCR, 진동 피드백을 연결한다.

처리 우선순위:
1. 장애물 경고
2. 목적지 근처 OCR 확인
3. 길안내 진동
4. 오류 피드백
"""

import time
from datetime import datetime, timezone

from actuators.vibration import (
    PATTERN_ARRIVED,
    PATTERN_ERROR,
    PATTERN_FRONT_OBSTACLE,
    PATTERN_LEFT,
    PATTERN_LEFT_OBSTACLE,
    PATTERN_NETWORK_ERROR,
    PATTERN_OCR_SEARCHING,
    PATTERN_PREPARE_LEFT,
    PATTERN_PREPARE_RIGHT,
    PATTERN_RIGHT,
    PATTERN_RIGHT_OBSTACLE,
    PATTERN_STRAIGHT,
    VibrationMotorController,
)
from ai.ocr import recognize_text
from config import (
    CAMERA_DEVICE_INDEX,
    CAMERA_FPS,
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    DEVICE_ID,
    NAVIGATION_SESSION_ID,
    GPS_BAUDRATE,
    GPS_PORT,
    GPS_TIMEOUT_SEC,
    LEFT_VIBRATION_PIN,
    LIDAR_CHANNELS,
    LIDAR_I2C_BUS_NUMBER,
    LOCATION_UPLOAD_INTERVAL_SEC,
    LOOP_INTERVAL_SEC,
    OCR_MATCH_REQUIRED_COUNT,
    OCR_RETRY_COUNT,
    RIGHT_VIBRATION_PIN,
    USER_ID,
)
from navigation.destination import (
    is_near_destination,
    is_ocr_matched,
)
from navigation.route_instruction import (
    ACTION_ARRIVED,
    ACTION_ERROR,
    ACTION_LEFT,
    ACTION_PREPARE_LEFT,
    ACTION_PREPARE_RIGHT,
    ACTION_RIGHT,
    ACTION_STRAIGHT,
    parse_navigation_instruction,
)
from network.api_client import (
    get_destination_list,
    get_navigation_instruction,
    save_location,
    save_ocr_result,
)
from obstacle_logic import (
    DANGER,
    WARNING,
    make_all_obstacle_statuses,
)
from sensors.camera import Camera
from sensors.gps import GpsReader
from sensors.lidar import MultiTFLunaLidar


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_first_destination():
    response = get_destination_list(USER_ID)

    if response.get("status") != "OK":
        return None

    data = response.get("data") or {}
    destinations = data.get("destinations") or []

    if not destinations:
        return None

    return destinations[0]


def get_obstacle_pattern(obstacle_statuses):
    front = obstacle_statuses.get("front")
    left = obstacle_statuses.get("left")
    right = obstacle_statuses.get("right")

    if front and front["risk_level"] in [DANGER, WARNING]:
        return PATTERN_FRONT_OBSTACLE

    if left and left["risk_level"] in [DANGER, WARNING]:
        return PATTERN_LEFT_OBSTACLE

    if right and right["risk_level"] in [DANGER, WARNING]:
        return PATTERN_RIGHT_OBSTACLE

    return None


def get_navigation_pattern(instruction):
    if instruction.action == ACTION_STRAIGHT:
        return PATTERN_STRAIGHT

    if instruction.action == ACTION_PREPARE_LEFT:
        return PATTERN_PREPARE_LEFT

    if instruction.action == ACTION_PREPARE_RIGHT:
        return PATTERN_PREPARE_RIGHT

    if instruction.action == ACTION_LEFT:
        return PATTERN_LEFT

    if instruction.action == ACTION_RIGHT:
        return PATTERN_RIGHT

    if instruction.action == ACTION_ARRIVED:
        return PATTERN_ARRIVED

    if instruction.action == ACTION_ERROR:
        return PATTERN_ERROR

    return None


def run_destination_ocr(camera, destination):
    target_text = destination.get("targetText", "")
    destination_id = destination.get("destinationId", "")

    match_count = 0
    best_result = None

    for _ in range(OCR_RETRY_COUNT):
        frame = camera.read_rgb()

        if frame is None:
            continue

        result = recognize_text(frame)
        best_result = result

        recognized_text = result.get("text", "")
        confidence = result.get("confidence", 0.0)

        if is_ocr_matched(recognized_text, target_text, confidence):
            match_count += 1

        if match_count >= OCR_MATCH_REQUIRED_COUNT:
            save_ocr_result(
                user_id=USER_ID,
                device_id=DEVICE_ID,
                destination_id=destination_id,
                recognized_text=recognized_text,
                target_text=target_text,
                confidence=confidence,
                matched=True,
                timestamp=now_iso(),
            )
            return True

        time.sleep(0.1)

    if best_result is not None:
        save_ocr_result(
            user_id=USER_ID,
            device_id=DEVICE_ID,
            destination_id=destination_id,
            recognized_text=best_result.get("text", ""),
            target_text=target_text,
            confidence=best_result.get("confidence", 0.0),
            matched=False,
            timestamp=now_iso(),
        )

    return False


def main():
    destination = get_first_destination()

    if destination is None:
        raise RuntimeError("destination is not available")

    lidar = MultiTFLunaLidar(
        bus_number=LIDAR_I2C_BUS_NUMBER,
        channels=LIDAR_CHANNELS,
    )

    gps = GpsReader(
        port=GPS_PORT,
        baudrate=GPS_BAUDRATE,
        timeout=GPS_TIMEOUT_SEC,
    )

    camera = Camera(
        device_index=CAMERA_DEVICE_INDEX,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        fps=CAMERA_FPS,
    )

    vibration = VibrationMotorController(
        left_pin=LEFT_VIBRATION_PIN,
        right_pin=RIGHT_VIBRATION_PIN,
    )

    last_location_upload_time = 0.0
    navigation_running = True

    try:
        gps.connect()
        camera.open()
        vibration.setup()

        while navigation_running:
            gps_location = gps.read_location()
            lidar_distances = lidar.read_all_distances_cm()
            obstacle_statuses = make_all_obstacle_statuses(lidar_distances)

            obstacle_pattern = get_obstacle_pattern(obstacle_statuses)

            if obstacle_pattern is not None:
                vibration.play_pattern(obstacle_pattern)
                time.sleep(LOOP_INTERVAL_SEC)
                continue

            if gps_location is not None and gps_location.get("valid"):
                current_time = time.time()

                if current_time - last_location_upload_time >= LOCATION_UPLOAD_INTERVAL_SEC:
                    save_location(
                        user_id=USER_ID,
                        device_id=DEVICE_ID,
                        latitude=gps_location["latitude"],
                        longitude=gps_location["longitude"],
                        timestamp=now_iso(),
                    )
                    last_location_upload_time = current_time

                if is_near_destination(gps_location, destination):
                    vibration.play_pattern(PATTERN_OCR_SEARCHING)
                    arrived = run_destination_ocr(camera, destination)

                    if arrived:
                        vibration.play_pattern(PATTERN_ARRIVED)
                        navigation_running = False
                        continue

            instruction_response = get_navigation_instruction(NAVIGATION_SESSION_ID)

            if instruction_response.get("status") == "ERROR":
                vibration.play_pattern(PATTERN_NETWORK_ERROR)
                time.sleep(LOOP_INTERVAL_SEC)
                continue

            instruction_data = instruction_response.get("data")
            instruction = parse_navigation_instruction(instruction_data)

            navigation_pattern = get_navigation_pattern(instruction)

            if navigation_pattern is not None:
                vibration.play_pattern(navigation_pattern)

            time.sleep(LOOP_INTERVAL_SEC)

    finally:
        lidar.close()
        gps.close()
        camera.close()
        vibration.cleanup()


if __name__ == "__main__":
    main()