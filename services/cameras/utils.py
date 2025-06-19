import cv2
import numpy as np
import os

def add_watermark(frame, logo_path="static/img/logo-senai.png", height=40, margin=10):
    if not os.path.exists(logo_path):
        return frame
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo is None:
        return frame

    # Redimensiona o logo para altura fixa, mantendo proporção
    h_logo = height
    w_logo = int(logo.shape[1] * (h_logo / logo.shape[0]))
    logo = cv2.resize(logo, (w_logo, h_logo), interpolation=cv2.INTER_AREA)

    y1 = frame.shape[0] - h_logo - margin
    x1 = frame.shape[1] - w_logo - margin
    y2 = y1 + h_logo
    x2 = x1 + w_logo

    # Se o logo tiver canal alpha, faz blending
    if logo.shape[2] == 4:
        alpha_logo = logo[:, :, 3] / 255.0
        for c in range(3):
            frame[y1:y2, x1:x2, c] = (
                logo[:, :, c] * alpha_logo + frame[y1:y2, x1:x2, c] * (1 - alpha_logo)
            ).astype(np.uint8)
    else:
        frame[y1:y2, x1:x2] = logo

    return frame