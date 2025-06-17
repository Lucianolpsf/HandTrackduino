import cv2
import time
import numpy as np
import mediapipe as mp
from . import servo_braco3d as mao

hands = mp.solutions.hands
Hands = hands.Hands(max_num_hands=1)
mpDwaw = mp.solutions.drawing_utils


def mao_aberta():
    mao.abrir_fechar(10, 1)
    mao.abrir_fechar(9, 1)
    mao.abrir_fechar(8, 1)
    mao.abrir_fechar(7, 0)
    mao.abrir_fechar(6, 0)

def gen_arduino_frames(camera_index):
    last_detected_time = time.time()
    in_rest_position = False
    cap = cv2.VideoCapture(int(camera_index))
    # cap.set(3, 1280)
    # cap.set(4, 720)

    try:
        while True:
            current_time = time.time()
            success, img = cap.read()
            if not success or img is None:
                print("Erro: Não foi possível capturar a imagem da câmera para o arduino!")
                break
            frameRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            results = Hands.process(frameRGB)
            handPoints = results.multi_hand_landmarks
            h, w, _ = img.shape
            pontos = []
            if handPoints:
                last_detected_time = current_time  # Atualiza porque detectou mão
                if in_rest_position:
                    print("Mão detectada novamente, saindo da posição de descanso.")
                    in_rest_position = False
                for points in handPoints:
                    mpDwaw.draw_landmarks(img, points,hands.HAND_CONNECTIONS)
                    for id, cord in enumerate(points.landmark):
                        cx, cy = int(cord.x * w), int(cord.y * h)
                        cv2.circle(img,(cx,cy),4,(255,0,0),-1)
                        pontos.append((cx,cy))

                    if pontos:
                        distPolegar = abs(pontos[17][0] - pontos[4][0])
                        distIndicador = pontos[5][1] - pontos[8][1]
                        distMedio = pontos[9][1] - pontos[12][1]
                        distAnelar = pontos[13][1] - pontos[16][1]
                        distMinimo = pontos[17][1] - pontos[20][1]

                        gesto_sinal_proibido = (
                            distMedio >= 1 and 
                            distIndicador < 5 and 
                            distAnelar < 5 and 
                            distMinimo < 1 and 
                            distPolegar >= 1
                        )
                        if gesto_sinal_proibido:
                            x, y, w_box, h_box = 30, 30, 400, 70
                            cv2.rectangle(img, (x, y), (x + w_box, y + h_box), (0, 0, 255), -1)
                            cv2.putText(img, 'SINAL PROIBIDO!', (x + 10, y + 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
                            mao_aberta()
                        else:
                            if distPolegar < 80:
                                mao.abrir_fechar(10, 0)
                            else:
                                mao.abrir_fechar(10, 1)

                            if distIndicador >= 1:
                                mao.abrir_fechar(9, 1)
                            else:
                                mao.abrir_fechar(9, 0)

                            if distMedio >= 1:
                                mao.abrir_fechar(8, 1)
                            else:
                                mao.abrir_fechar(8, 0)

                            if distAnelar >= 1:
                                mao.abrir_fechar(7, 0)
                            else:
                                mao.abrir_fechar(7, 1)

                            if distMinimo >= 1:
                                mao.abrir_fechar(6, 0)
                            else:
                                mao.abrir_fechar(6, 1)

            
            # Verifica inatividade
            if current_time - last_detected_time > 5:
                if not in_rest_position:
                    print("Nenhuma mão detectada por 5 segundos. Voltando para a posição padrão.")
                    mao.liberar_servos()
                    in_rest_position = True

            
            # Cria uma camada de sobreposição transparente
            overlay = img.copy()

            if current_time - last_detected_time > 5:
                # Estado de descanso
                texto = "Mao em Descanso"
                cor = (0, 0, 255)  # Vermelho
                posicao = (50, 50)
            else:
                texto = "Mao Detectada"
                cor = (0, 255, 0)  # Verde
                posicao = (50, 50)

            # Desenha um retângulo semi-transparente
            cv2.rectangle(overlay, (posicao[0]-10, posicao[1]-30), (posicao[0]+500, posicao[1]+10), (0,0,0), -1)

            # Faz blend entre a imagem original e o overlay
            alpha = 0.4
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

            # Coloca o texto por cima
            cv2.putText(img, texto, posicao, cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
     cap.release()
