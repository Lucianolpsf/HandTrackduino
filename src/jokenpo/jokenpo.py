from flask import Flask, render_template, Response, jsonify
from services.cameras.camera import listar_cameras_disponiveis
from services.github import get_cards
from src.robo.arduino import gen_arduino_frames
from src.desenho.lousa import gen_frames
import cv2
import mediapipe as mp
import random
import time
import numpy as np
app = Flask(__name__)


jokenpo_game_state = {
    "player_score": 0,
    "ai_score": 0,
    "ties": 0,
    "rounds_played": 0,
    "player_choice": "Nenhum",
    "ai_choice": "Nenhum",
    "result_message": "Aguardando...",
    "current_gesture_detected": "Nenhum",
    "hand_detected": False,
    "countdown_message": "",
    "game_phase": "waiting_start", # "waiting_start", "counting_down", "round_finished"
    "mediapipe_processing_active": False # Controlled by frontend buttons
}

# --- Game Control Timers (Global for persistence within the generator) ---
_timer_control_start = None
_tempo_espera_countdown = 3
_tempo_exibicao_resultado = 5

# MediaPipe initialization (global to avoid re-initialization per frame)
mp_hands_sol = mp.solutions.hands
hands_detector = mp_hands_sol.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- Jokenpo Game Logic Functions (from your original code) ---

def detectar_gesto(pontos):
    """
    Detects Rock, Paper, or Scissors from hand landmarks.
    """
    if len(pontos) < 21:
        return "Indefinido"

    distPolegar = abs(pontos[17][0] - pontos[4][0])
    distIndicador = pontos[5][1] - pontos[8][1]
    distMedio = pontos[9][1] - pontos[12][1]
    distAnelar = pontos[13][1] - pontos[16][1]
    distMinimo = pontos[17][1] - pontos[20][1]

    polegar_aberto = distPolegar >= 80
    indicador_aberto = distIndicador >= 1
    medio_aberto = distMedio >= 1
    anelar_aberto = distAnelar >= 1
    minimo_aberto = distMinimo >= 1

    dedos_abertos = [polegar_aberto, indicador_aberto, medio_aberto, anelar_aberto, minimo_aberto]

    if not any(dedos_abertos):
        return "Pedra"
    elif all(dedos_abertos):
        return "Papel"
    elif indicador_aberto and medio_aberto and not (polegar_aberto or anelar_aberto or minimo_aberto):
        return "Tesoura"
    else:
        return "Indefinido"

def escolher_jogada_robo():
    return random.choice(["Pedra", "Papel", "Tesoura"])

def resultado_jogo(jogador, robo):
    if jogador == "Indefinido":
        return "Mostre Pedra, Papel ou Tesoura claramente!"
    if jogador == robo:
        return "Empate!"
    elif (jogador == "Pedra" and robo == "Tesoura") or \
         (jogador == "Tesoura" and robo == "Papel") or \
         (jogador == "Papel" and robo == "Pedra"):
        return "Voce venceu!"
    else:
        return "Robo venceu!"

def gen_jokenpo_frames(camera_index=0):
    global jokenpo_game_state, _timer_control_start, _tempo_espera_countdown, _tempo_exibicao_resultado

    cap = cv2.VideoCapture(int(camera_index))
    if not cap.isOpened():
        print(f"Error: Could not open video stream for camera {camera_index}")
        jokenpo_game_state["camera_is_active"] = False
        img_error = 255 * np.ones((480, 640, 3), dtype=np.uint8)
        cv2.putText(img_error, "Camera Offline", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        ret, buffer = cv2.imencode('.jpg', img_error)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    jokenpo_game_state["camera_is_active"] = True

    while True:
        success, img = cap.read()
        if not success or img is None:
            print("Erro na captura da câmera ou fim do stream.")
            break 

        img = cv2.flip(img, 1) 

        frameRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        jokenpo_game_state["hand_detected"] = False
        pontos = []
        current_gesture_live_detection = "Nenhum"

        if jokenpo_game_state["mediapipe_processing_active"]:
            results = hands_detector.process(frameRGB)
            handPoints = results.multi_hand_landmarks

            if handPoints:
                jokenpo_game_state["hand_detected"] = True
                for points in handPoints:
                    mp_draw.draw_landmarks(img, points, mp_hands_sol.HAND_CONNECTIONS)
                    for id, lm in enumerate(points.landmark):
                        pontos.append((int(lm.x * img.shape[1]), int(lm.y * img.shape[0])))

                if pontos:
                    current_gesture_live_detection = detectar_gesto(pontos)
                else:
                    current_gesture_live_detection = "Indefinido"

            jokenpo_game_state["current_gesture_detected"] = current_gesture_live_detection

            # --- Game Phase Logic ---
            if jokenpo_game_state["game_phase"] == "counting_down":
                if _timer_control_start is None:
                    _timer_control_start = time.time()
                    jokenpo_game_state["result_message"] = "Contando..."
                    jokenpo_game_state["player_choice"] = "Nenhum"
                    jokenpo_game_state["ai_choice"] = "Nenhum"

                time_elapsed = time.time() - _timer_control_start
                segundos_restantes = int(_tempo_espera_countdown - time_elapsed) + 1

                if segundos_restantes > 0:
                    jokenpo_game_state["countdown_message"] = f"Jogue em... {segundos_restantes}"
                else:
                    jokenpo_game_state["countdown_message"] = "Jogada!"
                    jokenpo_game_state["game_phase"] = "round_finished"

                    jokenpo_game_state["player_choice"] = current_gesture_live_detection
                    ai_play = escolher_jogada_robo()
                    jokenpo_game_state["ai_choice"] = ai_play

                    result_msg = resultado_jogo(jokenpo_game_state["player_choice"], ai_play)
                    jokenpo_game_state["result_message"] = result_msg
                    jokenpo_game_state["rounds_played"] += 1

                    if "Voce venceu!" in result_msg:
                        jokenpo_game_state["player_score"] += 1
                    elif "Robo venceu!" in result_msg:
                        jokenpo_game_state["ai_score"] += 1
                    elif "Empate!" in result_msg:
                        jokenpo_game_state["ties"] += 1

                    _timer_control_start = time.time() # Start timer for result display

            elif jokenpo_game_state["game_phase"] == "round_finished":
                if _timer_control_start is not None and (time.time() - _timer_control_start) > _tempo_exibicao_resultado:
                    jokenpo_game_state["game_phase"] = "waiting_start"
                    jokenpo_game_state["countdown_message"] = ""
                    jokenpo_game_state["result_message"] = "Aguardando..."
                    jokenpo_game_state["player_choice"] = "Nenhum"
                    jokenpo_game_state["ai_choice"] = "Nenhum"
                    _timer_control_start = None

            elif jokenpo_game_state["game_phase"] == "waiting_start":
                jokenpo_game_state["result_message"] = "Pressione 'Jogar Rodada' para comecar!"
                jokenpo_game_state["countdown_message"] = ""
                jokenpo_game_state["player_choice"] = "Nenhum"
                jokenpo_game_state["ai_choice"] = "Nenhum"
                _timer_control_start = None

        else: # MediaPipe processing is NOT active
            jokenpo_game_state["hand_detected"] = False
            jokenpo_game_state["current_gesture_detected"] = "Nenhum"
            jokenpo_game_state["countdown_message"] = ""
            jokenpo_game_state["game_phase"] = "waiting_start" # Reset to initial state
            jokenpo_game_state["result_message"] = "Processamento Inativo. Ative para jogar."
            jokenpo_game_state["player_choice"] = "Nenhum"
            jokenpo_game_state["ai_choice"] = "Nenhum"
            _timer_control_start = None

        # --- Overlay Text on OpenCV Frame ---
        h, w, _ = img.shape
        text_y_start = h - 130

        # Scoreboard
        cv2.putText(img,
                    f'J:{jokenpo_game_state["player_score"]} | IA:{jokenpo_game_state["ai_score"]} | E:{jokenpo_game_state["ties"]}',
                    (int(w/2) - 130, text_y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Countdown Message
        if jokenpo_game_state["countdown_message"]:
            (text_width, text_height) = cv2.getTextSize(jokenpo_game_state["countdown_message"], cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            text_x = int((w - text_width) / 2)
            cv2.putText(img, jokenpo_game_state["countdown_message"],
                        (text_x, text_y_start + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

        # Result Message
        (result_width, result_height) = cv2.getTextSize(jokenpo_game_state["result_message"], cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        result_x = int((w - result_width) / 2)

        cor_resultado = (150, 0, 255)
        if "Voce venceu!" in jokenpo_game_state["result_message"]:
            cor_resultado = (0, 255, 0)
        elif "Robo venceu!" in jokenpo_game_state["result_message"]:
            cor_resultado = (0, 0, 255)
        elif "Empate!" in jokenpo_game_state["result_message"]:
            cor_resultado = (255, 255, 0)

        cv2.putText(img, jokenpo_game_state["result_message"],
                    (result_x, text_y_start + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, cor_resultado, 2)

        # Player's current gesture
        cv2.putText(img, f'Sua jogada: {jokenpo_game_state["current_gesture_detected"]}',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        # AI's choice (only shown when available)
        ai_display_choice = jokenpo_game_state["ai_choice"] if jokenpo_game_state["game_phase"] == "round_finished" else "..."
        cv2.putText(img, f'Jogada IA: {ai_display_choice}',
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
