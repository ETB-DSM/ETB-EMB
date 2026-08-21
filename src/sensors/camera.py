"""USB 카메라에서 영상 프레임을 가져오는 파일.

카메라 장치 번호를 확인한 뒤 OpenCV로 프레임을 읽고, YOLO나 OCR 코드에
전달할 이미지 데이터를 만든다.
"""

import cv2


class Camera:
    def __init__(self, device_index: int = 0, width: int = 640, height: int = 480, fps: int = 30):
        self.device_index = device_index
        self.width = width
        self.height = height
        self.fps = fps
        self.capture = None

    def open(self):
        self.capture = cv2.VideoCapture(self.device_index, cv2.CAP_V4L2)

        if not self.capture.isOpened():
            self.capture = cv2.VideoCapture(self.device_index)

        if not self.capture.isOpened():
            raise RuntimeError(f"cannot open camera index {self.device_index}")

        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))	
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)

    def is_opened(self):
        return self.capture is not None and self.capture.isOpened()

    def read_frame(self):
        if self.capture is None:
            raise RuntimeError("camera is not opened")

        ret, frame = self.capture.read()

        if not ret:
            return None

        return frame

    def read_rgb(self):
        frame = self.read_frame()

        if frame is None:
            return None

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def close(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
