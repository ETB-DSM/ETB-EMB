"""목적지 판단 보조 파일.

사용자가 목적지 근처에 있는지, OCR 결과가 목적지 targetText와 일치하는지
판단한다.

이 파일은 GPS를 직접 읽지 않는다.
OCR도 직접 실행하지 않는다.
데이터를 입력받아 판단 결과만 반환한다.
"""

import math


DEFAULT_ARRIVAL_RADIUS_M = 30
DEFAULT_OCR_CONFIDENCE_THRESHOLD = 0.6


def calculate_distance_meters(lat1, lon1, lat2, lon2):
    earth_radius_m = 6371000

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) * math.sin(dlat / 2)
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(dlon / 2)
        * math.sin(dlon / 2)
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius_m * c


def is_valid_location(location):
    if location is None:
        return False

    latitude = location.get("latitude")
    longitude = location.get("longitude")

    if latitude is None or longitude is None:
        return False

    if not (-90 <= latitude <= 90):
        return False

    if not (-180 <= longitude <= 180):
        return False

    return True


def get_destination_radius(destination):
    radius = destination.get(
        "radius",
        destination.get("arrival_radius_m", DEFAULT_ARRIVAL_RADIUS_M),
    )

    try:
        return float(radius)
    except (TypeError, ValueError):
        return DEFAULT_ARRIVAL_RADIUS_M


def get_distance_to_destination(location, destination):
    if not is_valid_location(location):
        return None

    if destination is None:
        return None

    destination_latitude = destination.get("latitude")
    destination_longitude = destination.get("longitude")

    if destination_latitude is None or destination_longitude is None:
        return None

    return calculate_distance_meters(
        location["latitude"],
        location["longitude"],
        destination_latitude,
        destination_longitude,
    )


def is_near_destination(location, destination):
    distance_meters = get_distance_to_destination(location, destination)

    if distance_meters is None:
        return False

    radius_meters = get_destination_radius(destination)

    return distance_meters <= radius_meters


def normalize_text(text):
    if text is None:
        return ""

    return str(text).replace(" ", "").lower()


def is_ocr_matched(
    recognized_text,
    target_text,
    confidence,
    confidence_threshold=DEFAULT_OCR_CONFIDENCE_THRESHOLD,
):
    if recognized_text is None:
        return False

    if target_text is None:
        return False

    try:
        confidence_value = float(confidence)
    except (TypeError, ValueError):
        return False

    if confidence_value < confidence_threshold:
        return False

    normalized_recognized_text = normalize_text(recognized_text)
    normalized_target_text = normalize_text(target_text)

    if not normalized_recognized_text:
        return False

    if not normalized_target_text:
        return False

    return normalized_target_text in normalized_recognized_text


def make_destination_status(location, destination):
    distance_meters = get_distance_to_destination(location, destination)

    if distance_meters is None:
        return {
            "valid": False,
            "near_destination": False,
            "distance_meters": None,
            "radius_meters": None,
        }

    radius_meters = get_destination_radius(destination)

    return {
        "valid": True,
        "near_destination": distance_meters <= radius_meters,
        "distance_meters": distance_meters,
        "radius_meters": radius_meters,
    }