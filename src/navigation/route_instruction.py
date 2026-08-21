"""길안내 명령 파싱 파일.

앱 또는 서버에서 받은 길안내 데이터를 Orange Pi가 진동 피드백에 사용할 수 있는
간단한 action 값으로 변환한다.

이 파일은 진동모터를 직접 제어하지 않는다.
직진, 회전 준비, 즉시 회전, 도착 같은 길안내 상태만 판단한다.
"""

from dataclasses import dataclass


ACTION_NONE = "none"
ACTION_STRAIGHT = "straight"
ACTION_PREPARE_LEFT = "prepare_left"
ACTION_PREPARE_RIGHT = "prepare_right"
ACTION_LEFT = "left"
ACTION_RIGHT = "right"
ACTION_ARRIVED = "arrived"
ACTION_REROUTE = "reroute"
ACTION_ERROR = "error"

TURN_PREPARE_DISTANCE_M = 20
TURN_NOW_DISTANCE_M = 5


VALID_ACTIONS = {
    ACTION_NONE,
    ACTION_STRAIGHT,
    ACTION_PREPARE_LEFT,
    ACTION_PREPARE_RIGHT,
    ACTION_LEFT,
    ACTION_RIGHT,
    ACTION_ARRIVED,
    ACTION_REROUTE,
    ACTION_ERROR,
}


@dataclass
class NavigationInstruction:
    action: str
    distance_meters: float | None = None
    message: str = ""
    raw_action: str = ""


def _to_float_or_none(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_turn_action(action, distance_meters):
    if action not in [ACTION_LEFT, ACTION_RIGHT]:
        return action

    if distance_meters is None:
        return action

    if distance_meters <= TURN_NOW_DISTANCE_M:
        return action

    if distance_meters <= TURN_PREPARE_DISTANCE_M:
        if action == ACTION_LEFT:
            return ACTION_PREPARE_LEFT

        if action == ACTION_RIGHT:
            return ACTION_PREPARE_RIGHT

    return ACTION_STRAIGHT


def parse_navigation_instruction(data):
    if data is None:
        return NavigationInstruction(
            action=ACTION_NONE,
            message="길안내 명령이 비어 있습니다",
        )

    action = str(data.get("action", ACTION_NONE)).strip().lower()
    distance_meters = _to_float_or_none(data.get("distanceMeters"))
    message = str(data.get("message", ""))

    if action not in VALID_ACTIONS:
        return NavigationInstruction(
            action=ACTION_ERROR,
            distance_meters=distance_meters,
            message=f"알 수 없는 길안내 action입니다: {action}",
            raw_action=action,
        )

    normalized_action = _normalize_turn_action(action, distance_meters)

    return NavigationInstruction(
        action=normalized_action,
        distance_meters=distance_meters,
        message=message,
        raw_action=action,
    )


def is_turn_action(action):
    return action in [ACTION_LEFT, ACTION_RIGHT]


def is_prepare_turn_action(action):
    return action in [ACTION_PREPARE_LEFT, ACTION_PREPARE_RIGHT]


def is_navigation_active(action):
    return action not in [ACTION_NONE, ACTION_ARRIVED, ACTION_ERROR]