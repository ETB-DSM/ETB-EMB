"""카메라 이미지에서 글자를 인식하는 OCR 기능 파일.

목적지 이름, 표지판, 간판 같은 텍스트를 읽어 목적지 확인 기능에 사용할
OCR 결과를 생성한다.
"""

from __future__ import annotations

import logging
import time

import cv2
import numpy as np

logger = logging.getLogger("ai_cane.ocr")

# ---------------------------------------------------------------------------
# 설정값
# ---------------------------------------------------------------------------
# PaddleOCR 언어팩: "korean"은 한글 + 영어 + 숫자를 한 모델로 함께 인식한다.
_OCR_LANG = "korean"

# 인식 신뢰도(0~1)가 이 값보다 낮은 결과는 잡음으로 보고 버린다.
_DEFAULT_MIN_CONFIDENCE = 0.5

# 오렌지파이는 GPU가 없고 RAM이 4GB로 제한적이므로, 입력 이미지의 긴 변을
# 이 값 이하로 줄여서 연산량과 메모리 사용량을 낮춘다. (기본값 960 -> 640)
_DET_LIMIT_SIDE_LEN = 640

# 검출/인식에 사용할 CPU 스레드 수. 오렌지파이 코어 수에 맞춰 조정 가능.
_CPU_THREADS = 4

_engine = None  # PaddleOCR 인스턴스. 최초 호출 시 한 번만 만들어 재사용한다.


def _get_engine():
    """PaddleOCR 엔진을 지연 생성해서 재사용한다.

    모델 로딩이 오렌지파이에서 수 초 걸리고 메모리도 쓰므로, 매 호출마다
    새로 만들지 않고 프로세스당 한 번만 만든다.
    """
    global _engine
    if _engine is None:
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(
                "paddleocr가 설치되어 있지 않습니다. "
                "'pip install \"paddleocr<3\" paddlepaddle' 로 설치하세요."
            ) from exc

        logger.info("PaddleOCR 엔진 로딩 중 (lang=%s)...", _OCR_LANG)
        _engine = PaddleOCR(
            lang=_OCR_LANG,
            use_gpu=False,
            use_angle_cls=False,  # 기울어진 글자 보정 생략 -> 속도/메모리 절약
            det_limit_side_len=_DET_LIMIT_SIDE_LEN,
            cpu_threads=_CPU_THREADS,
            show_log=False,
        )
        logger.info("PaddleOCR 엔진 로딩 완료")
    return _engine


def recognize_text(image: np.ndarray, min_confidence: float = _DEFAULT_MIN_CONFIDENCE) -> dict:
    """RGB 이미지 한 장에서 글자를 인식한다.

    Args:
        image: camera.read_rgb()가 반환하는 numpy 배열. shape=(H, W, 3),
            RGB 순서, 0~255 값 범위.
        min_confidence: 이 값보다 신뢰도가 낮은 결과는 최종 텍스트에서 뺀다.

    Returns:
        {
            "text": str,        인식된 전체 텍스트 (여러 줄은 공백으로 연결)
            "confidence": float,  인식된 줄들의 평균 신뢰도 (없으면 0.0)
            "lines": [          줄 단위 상세 결과
                {"text": str, "confidence": float, "box": [[x, y], ...]},
                ...
            ],
        }
    """
    if image is None or image.size == 0:
        logger.warning("빈 이미지가 들어와 OCR을 건너뜁니다.")
        return {"text": "", "confidence": 0.0, "lines": []}

    # PaddleOCR은 cv2.imread와 같은 BGR 순서를 기대하므로, camera.read_rgb()가
    # 주는 RGB 이미지를 여기서 BGR로 바꿔준다.
    bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    engine = _get_engine()

    start = time.monotonic()
    raw = engine.ocr(bgr_image, cls=False)
    elapsed = time.monotonic() - start

    lines = []
    # PaddleOCR은 이미지가 1장이어도 [[...]] 형태(이미지별 리스트)로 반환한다.
    page = raw[0] if raw else []
    for box, (text, confidence) in page or []:
        if confidence < min_confidence:
            continue
        lines.append({"text": text, "confidence": float(confidence), "box": box})

    combined_text = " ".join(line["text"] for line in lines)
    avg_confidence = sum(line["confidence"] for line in lines) / len(lines) if lines else 0.0

    logger.info("OCR 완료: %d줄 인식, %.2f초 소요", len(lines), elapsed)
    return {"text": combined_text, "confidence": avg_confidence, "lines": lines}


if __name__ == "__main__":
    # 단독 실행 테스트용: USB 카메라(장치 0번)에서 한 프레임을 찍어 OCR을 돌려본다.
    # 실제 임베디드 실행에서는 camera.read_rgb()가 이미지를 제공하고, 이
    # 블록은 이 파일만 따로 테스트할 때만 쓰인다.
    logging.basicConfig(level=logging.INFO)

    cap = cv2.VideoCapture(0)
    ok, bgr_frame = cap.read()
    cap.release()

    if not ok:
        logger.error("USB 카메라에서 프레임을 읽지 못했습니다.")
    else:
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)  # camera.read_rgb()와 동일한 형태
        result = recognize_text(rgb_frame)
        print("인식된 텍스트:", result["text"])
        print("평균 신뢰도:", result["confidence"])
        for line in result["lines"]:
            print(f"  - {line['text']!r} (신뢰도 {line['confidence']:.2f})")