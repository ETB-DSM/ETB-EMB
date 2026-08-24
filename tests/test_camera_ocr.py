"""USB 카메라 프레임을 OCR로 바로 넘기는 테스트 실행 파일.

이미지 파일을 저장하고, 실제 main.py 흐름처럼 카메라 프레임을 읽은 뒤
OCR 결과를 터미널에 출력한다. 매 OCR 직전에 오래된 카메라 버퍼를 버리고
최신 프레임을 사용해서 이전 명찰 결과가 남는 현상을 줄인다.
"""

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import sys
import time

import cv2

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from ai.ocr import recognize_text
from config import CAMERA_FPS, CAMERA_HEIGHT, CAMERA_WIDTH
from sensors.camera import Camera

try:
    from config import CAMERA_DEVICE_INDEX
except ImportError:
    from config import CAMERA_INDEX as CAMERA_DEVICE_INDEX


def read_camera_frame(camera: Camera):
    """Camera 클래스 버전 차이를 흡수해서 프레임을 읽는다."""
    if hasattr(camera, "capture_frame"):
        return camera.capture_frame()
    if hasattr(camera, "read_frame"):
        return camera.read_frame()
    raise RuntimeError("Camera class has no frame read method")


def read_fresh_camera_frame(camera: Camera, discard_count: int):
    """카메라 버퍼에 남아 있는 이전 프레임을 버리고 최신 프레임을 읽는다."""
    frame = None

    for _ in range(max(0, discard_count)):
        frame = read_camera_frame(camera)

    latest_frame = read_camera_frame(camera)
    if latest_frame is not None:
        return latest_frame

    return frame


def normalize_ocr_result(result: dict) -> dict:
    """OCR 결과 key 이름 차이를 흡수해서 표준 형태로 맞춘다."""
    recognized_text = (
        result.get("recognizedText")
        or result.get("recognized_text")
        or result.get("text")
        or ""
    )

    confidence = (
        result.get("confidence")
        or result.get("average_confidence")
        or result.get("score")
        or 0.0
    )

    return {
        "recognizedText": recognized_text.strip(),
        "confidence": float(confidence),
        "raw": result,
    }


def save_frame(frame, count: int) -> Path:
    """OCR에 사용한 프레임을 이미지 파일로 저장한다."""
    output_dir = BASE_DIR / "captures"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"ocr_frame_{timestamp}_{count}.jpg"

    cv2.imwrite(str(output_path), frame)

    return output_path


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--camera-index", type=int, default=CAMERA_DEVICE_INDEX)
    parser.add_argument("--width", type=int, default=CAMERA_WIDTH)
    parser.add_argument("--height", type=int, default=CAMERA_HEIGHT)
    parser.add_argument("--fps", type=int, default=CAMERA_FPS)
    parser.add_argument("--target-text", default="")
    parser.add_argument("--interval-sec", type=float, default=1.0)
    parser.add_argument("--max-count", type=int, default=0)
    parser.add_argument("--discard-frames", type=int, default=8)
    parser.add_argument("--min-confidence", type=float, default=0.5)
    args = parser.parse_args()

    camera = Camera(
        device_index=args.camera_index,
        width=args.width,
        height=args.height,
        fps=args.fps,
    )

    try:
        camera.open()

        if getattr(camera, "capture", None) is not None:
            camera.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print("camera_ocr: started")
        print("camera_ocr: press Ctrl+C to stop")
        print(f"camera_ocr: discard_frames={args.discard_frames}")

        count = 0

        while True:
            capture_started_at = time.time()
            frame = read_fresh_camera_frame(camera, args.discard_frames)

            if frame is None:
                print(f"ocr[{count}] frame=empty")
                time.sleep(args.interval_sec)
                continue

            saved_path = save_frame(frame, count)

            result = normalize_ocr_result(recognize_text(frame))
            recognized_text = result["recognizedText"]
            confidence = result["confidence"]

            if confidence < args.min_confidence:
                recognized_text = ""

            matched = bool(args.target_text and args.target_text in recognized_text)
            elapsed_sec = time.time() - capture_started_at
            display_text = recognized_text if recognized_text else "인식 실패"

            print(
                f"ocr[{count}] "
                f"text={display_text} "
                f"confidence={confidence:.3f} "
                f"elapsed={elapsed_sec:.2f}s "
                f"target={args.target_text} "
                f"matched={matched} "
                f"saved={saved_path}"
            )

            count += 1

            if args.max_count > 0 and count >= args.max_count:
                break

            time.sleep(args.interval_sec)

    except KeyboardInterrupt:
        print("camera_ocr: stopped")

    finally:
        camera.close()


if __name__ == "__main__":
    main()