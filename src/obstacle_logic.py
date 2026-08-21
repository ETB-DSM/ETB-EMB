"""장애물 판단 로직 파일.

LiDAR 거리값을 장애물 위험 단계로 변환한다.

이 파일은 LiDAR를 직접 읽지 않는다.
진동모터도 직접 제어하지 않는다.
거리 데이터를 입력받아 장애물 판단 결과만 반환한다.
"""

UNKNOWN = "unknown"
SAFE = "safe"
NOTICE = "notice"
WARNING = "warning"
DANGER = "danger"

DANGER_DISTANCE_CM = 50
WARNING_DISTANCE_CM = 100
NOTICE_DISTANCE_CM = 150

IMPORTANT_DIRECTIONS = ["front", "left", "right"]
ALL_DIRECTIONS = ["front", "left", "right", "upper", "lower"]


def classify_distance(distance_cm):
    if distance_cm is None:
        return UNKNOWN

    try:
        distance = float(distance_cm)
    except (TypeError, ValueError):
        return UNKNOWN

    if distance <= 0:
        return UNKNOWN

    if distance <= DANGER_DISTANCE_CM:
        return DANGER

    if distance <= WARNING_DISTANCE_CM:
        return WARNING

    if distance <= NOTICE_DISTANCE_CM:
        return NOTICE

    return SAFE


def is_obstacle_detected(risk_level):
    return risk_level in [NOTICE, WARNING, DANGER]


def is_dangerous_obstacle(risk_level):
    return risk_level in [WARNING, DANGER]


def make_obstacle_status(direction, distance_cm):
    risk_level = classify_distance(distance_cm)

    return {
        "direction": direction,
        "distance_cm": distance_cm,
        "risk_level": risk_level,
        "obstacle_detected": is_obstacle_detected(risk_level),
        "dangerous": is_dangerous_obstacle(risk_level),
    }


def make_all_obstacle_statuses(distances):
    statuses = {}

    for direction, distance_cm in distances.items():
        statuses[direction] = make_obstacle_status(direction, distance_cm)

    return statuses


def get_nearest_obstacle(statuses):
    valid_statuses = []

    for status in statuses.values():
        distance_cm = status.get("distance_cm")

        if distance_cm is None:
            continue

        try:
            distance = float(distance_cm)
        except (TypeError, ValueError):
            continue

        if distance <= 0:
            continue

        valid_statuses.append(status)

    if not valid_statuses:
        return None

    return min(valid_statuses, key=lambda status: float(status["distance_cm"]))


def get_highest_priority_obstacle(statuses):
    for direction in IMPORTANT_DIRECTIONS:
        status = statuses.get(direction)

        if status is None:
            continue

        if status["risk_level"] == DANGER:
            return status

    for direction in IMPORTANT_DIRECTIONS:
        status = statuses.get(direction)

        if status is None:
            continue

        if status["risk_level"] == WARNING:
            return status

    for direction in ["upper", "lower"]:
        status = statuses.get(direction)

        if status is None:
            continue

        if status["risk_level"] in [DANGER, WARNING]:
            return status

    return None


def has_dangerous_obstacle(statuses):
    return get_highest_priority_obstacle(statuses) is not None