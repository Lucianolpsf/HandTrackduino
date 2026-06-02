import cv2
import threading
from services.cameras.camera_manager import CameraManager


def try_open_camera(index, result, timeout=50.0):
    """
    Tenta abrir a câmera no índice especificado com timeout.
    Se conseguir abrir, adiciona o índice à lista result.
    """
    def target():
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            result.append(index)
            cap.release()
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return

def listar_cameras_disponiveis(max_index=5, timeout=50.0):
    CameraManager.get_instance().release()  # Libera antes de listar
    cameras = []
    for i in range(max_index):
        try_open_camera(i, cameras, timeout)
    return cameras