"""백엔드 API 통신 파일.

Orange Pi와 백엔드 서버 사이에서 사용자, 목적지, 위치, OCR, SOS,
디바이스 상태, 길안내 명령 데이터를 주고받는다.
"""

import requests

from config import API_TIMEOUT_SEC, SERVER_BASE_URL


def _status_to_bool(value):
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    return str(value).strip().lower() in ["ok", "true", "1", "yes"]


def request_api(method, path, json_data=None, params=None):
    url = f"{SERVER_BASE_URL}{path}"

    try:
        response = requests.request(
            method=method,
            url=url,
            json=json_data,
            params=params,
            timeout=API_TIMEOUT_SEC,
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        return {
            "status": "ERROR",
            "message": "api request timeout",
            "data": None,
        }

    except requests.exceptions.ConnectionError:
        return {
            "status": "ERROR",
            "message": "api connection error",
            "data": None,
        }

    except requests.exceptions.HTTPError:
        try:
            return response.json()
        except ValueError:
            return {
                "status": "ERROR",
                "message": f"http error: {response.status_code}",
                "data": None,
            }

    except ValueError:
        return {
            "status": "ERROR",
            "message": "invalid api response json",
            "data": None,
        }


def update_device_status(
    user_id,
    device_id,
    battery,
    lidar_status,
    camera_status,
    gps_status,
    network_status,
    timestamp,
):
    data = {
        "deviceId": device_id,
        "battery": battery,
        "lidarOk": _status_to_bool(lidar_status),
        "cameraOk": _status_to_bool(camera_status),
        "gpsOk": _status_to_bool(gps_status),
        "networkOk": _status_to_bool(network_status),
    }

    return request_api("POST", "/api/device/status", json_data=data)


def save_ocr_result(
    user_id,
    device_id,
    destination_id,
    recognized_text,
    target_text,
    confidence,
    matched,
    timestamp,
):
    data = {
        "destinationId": destination_id,
        "recognizedText": recognized_text,
        "targetText": target_text,
        "matched": matched,
        "confidence": confidence,
    }

    return request_api("POST", "/api/ocr/results", json_data=data)


def save_location(user_id, device_id, latitude, longitude, timestamp):
    data = {
        "userId": user_id,
        "deviceId": device_id,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp,
    }

    return request_api("POST", "/api/location", json_data=data)


def create_destination(user_id, name, target_text, latitude, longitude, radius):
    data = {
        "userId": user_id,
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "radiusM": radius,
        "targetText": target_text,
    }

    return request_api("POST", "/api/destinations", json_data=data)


def register_user(user_id, name, guardian_name, guardian_phone, device_id):
    data = {
        "userId": user_id,
        "name": name,
        "guardianName": guardian_name,
        "guardianPhone": guardian_phone,
        "deviceId": device_id,
    }

    return request_api("POST", "/api/users", json_data=data)


def get_destination_list(user_id):
    return request_api(
        "GET",
        "/api/destinations",
        params={"userId": user_id},
    )


def check_device_status(device_id):
    path = f"/api/device/status/{device_id}"
    return request_api("GET", path)


def check_user(user_id):
    path = f"/api/users/{user_id}"
    return request_api("GET", path)


def send_sos(
    user_id,
    device_id,
    event_type,
    latitude,
    longitude,
    battery,
    timestamp,
):
    data = {
        "userId": user_id,
        "deviceId": device_id,
        "eventType": event_type,
        "latitude": latitude,
        "longitude": longitude,
        "battery": battery,
        "timestamp": timestamp,
    }

    return request_api("POST", "/api/sos", json_data=data)


def create_navigation_session(
    user_id,
    device_id,
    destination_id,
    start_latitude,
    start_longitude,
    timestamp,
):
    data = {
        "destinationId": destination_id,
        "deviceId": device_id,
        "startLatitude": start_latitude,
        "startLongitude": start_longitude,
    }

    return request_api("POST", "/api/navigation/sessions", json_data=data)


def get_navigation_instruction(navigation_session_id):
    path = f"/api/navigation/sessions/{navigation_session_id}/instruction"
    return request_api("GET", path)


def update_navigation_session_status(
    navigation_session_id,
    status,
    reason,
    timestamp,
):
    data = {
        "status": status,
        "reason": reason,
    }

    path = f"/api/navigation/sessions/{navigation_session_id}/status"
    return request_api("PATCH", path, json_data=data)
