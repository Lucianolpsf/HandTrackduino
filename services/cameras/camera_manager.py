import cv2
import threading

class CameraManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.cap = None
        self.index = None

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = CameraManager()
            return cls._instance

    def set_camera(self, index):
        with self._lock:
            if self.cap is not None:
                self.cap.release()
            self.cap = cv2.VideoCapture(index)
            self.index = index

    def get_frame(self):
        with self._lock:
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    return frame
            return None

    def release(self):
        with self._lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
                self.index = None