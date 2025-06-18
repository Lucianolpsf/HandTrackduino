import cv2
import mediapipe as mp
import random
import time
import threading
import numpy as np # Para lidar com imagens NumPy (erros da câmera)

# --- IMPORTANTE: Importar o módulo de controle do braço robótico ---
# A pasta 'jokenpo' já tem um 'servo_braco3d.py', então usamos importação relativa
from . import servo_braco3d as mao 

# --- ESTADO GLOBAL DO JOGO JOKENPO (Centralizado neste módulo) ---
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
    "game_phase": "waiting_start",  # "waiting_start", "counting_down", "round_finished"
    "mediapipe_processing_active": False, # Controlado por funções de fora
    "camera_is_active": False, # Estado da câmera
}

# --- Variáveis de Controle de Temporização do Jokenpo ---
# Usadas internamente na thread de processamento.
_timer_control_start = None
_tempo_espera_countdown = 3  # Segundos para a contagem regressiva da jogada
_tempo_exibicao_resultado = 5  # Segundos para exibir o resultado final

# --- Inicialização do MediaPipe (Global para este módulo) ---
mp_hands_sol = mp.solutions.hands
hands_detector = mp_hands_sol.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- Funções de Lógica do Jogo Jokenpo ---
def detectar_gesto(pontos):
    """
    Tenta determinar a jogada de Jokenpo a partir dos pontos da mão.
    Retorna "Pedra", "Papel", "Tesoura" ou "Indefinido".
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
    """O robô escolhe aleatoriamente Pedra, Papel ou Tesoura."""
    return random.choice(["Pedra", "Papel", "Tesoura"])

def resultado_jogo(jogador, robo):
    """Determina o resultado do jogo."""
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

# --- Funções de Controle da Mão Robótica (utilizando servo_braco3d) ---
def posicao_neutra_robo():
    """Define a mão robótica para uma posição neutra (todos os dedos fechados)."""
    try:
        mao.abrir_fechar(10, 0) # Polegar fechado
        mao.abrir_fechar(9, 0)  # Indicador fechado
        mao.abrir_fechar(8, 0)  # Médio fechado
        mao.abrir_fechar(7, 0)  # Anelar fechado
        mao.abrir_fechar(6, 0)  # Mínimo fechado
        # print("[ROBO JOKENPO] Mão robótica na posição neutra.") # Descomente para depuração
    except Exception as e:
        print(f"[ROBO JOKENPO ERRO] Falha ao definir posição neutra: {e}")

def fazer_pedra_robo():
    """Define a mão robótica para o gesto de 'Pedra'."""
    try:
        mao.abrir_fechar(10, 0) # Polegar fechado
        mao.abrir_fechar(9, 0)  # Indicador fechado
        mao.abrir_fechar(8, 0)  # Médio fechado
        mao.abrir_fechar(7, 0)  # Anelar fechado
        mao.abrir_fechar(6, 0)  # Mínimo fechado
        # print("[ROBO JOKENPO] Mão robótica fez PEDRA.") # Descomente para depuração
    except Exception as e:
        print(f"[ROBO JOKENPO ERRO] Falha ao fazer Pedra: {e}")

def fazer_papel_robo():
    """Define a mão robótica para o gesto de 'Papel'."""
    try:
        mao.abrir_fechar(10, 1) # Polegar aberto
        mao.abrir_fechar(9, 1)  # Indicador aberto
        mao.abrir_fechar(8, 1)  # Médio aberto
        mao.abrir_fechar(7, 1)  # Anelar aberto
        mao.abrir_fechar(6, 1)  # Mínimo aberto
        # print("[ROBO JOKENPO] Mão robótica fez PAPEL.") # Descomente para depuração
    except Exception as e:
        print(f"[ROBO JOKENPO ERRO] Falha ao fazer Papel: {e}")

def fazer_tesoura_robo():
    """Define a mão robótica para o gesto de 'Tesoura'."""
    try:
        mao.abrir_fechar(10, 0) # Polegar fechado
        mao.abrir_fechar(9, 1)  # Indicador aberto
        mao.abrir_fechar(8, 1)  # Médio aberto
        mao.abrir_fechar(7, 0)  # Anelar fechado
        mao.abrir_fechar(6, 0)  # Mínimo fechado
        # print("[ROBO JOKENPO] Mão robótica fez TESOURA.") # Descomente para depuração
    except Exception as e:
        print(f"[ROBO JOKENPO ERRO] Falha ao fazer Tesoura: {e}")

# --- Funções de Interface para o Flask (para controlar o estado do jogo) ---
def get_jokenpo_game_state_data():
    """Retorna uma cópia do estado atual do jogo Jokenpo."""
    return jokenpo_game_state.copy()

def start_jokenpo_round_logic():
    """Inicia a contagem regressiva para uma nova rodada de Jokenpo."""
    global jokenpo_game_state, _timer_control_start
    if jokenpo_game_state["mediapipe_processing_active"] and jokenpo_game_state["game_phase"] == "waiting_start":
        _timer_control_start = time.time() # Inicia o timer
        jokenpo_game_state["game_phase"] = "counting_down"
        jokenpo_game_state["result_message"] = "Contagem iniciada..."
        jokenpo_game_state["player_choice"] = "Nenhum"
        jokenpo_game_state["ai_choice"] = "Nenhum"
        jokenpo_game_state["countdown_message"] = "" 
        posicao_neutra_robo() # Garante mão neutra no início da contagem
        return {"status": "success", "message": "Rodada de Jokenpo iniciada."}
    else:
        status_msg = "Processamento da mão não ativo ou rodada já em andamento."
        if not jokenpo_game_state["mediapipe_processing_active"]:
            status_msg = "Por favor, ative o processamento da mão antes de jogar."
        elif jokenpo_game_state["game_phase"] != "waiting_start":
            status_msg = "Uma rodada já está em andamento. Aguarde ou reinicie."
        return {"status": "error", "message": status_msg}

def reset_jokenpo_score_logic():
    """Reseta o placar do Jokenpo."""
    global jokenpo_game_state, _timer_control_start
    jokenpo_game_state["player_score"] = 0
    jokenpo_game_state["ai_score"] = 0
    jokenpo_game_state["ties"] = 0 
    jokenpo_game_state["rounds_played"] = 0
    jokenpo_game_state["player_choice"] = "Nenhum"
    jokenpo_game_state["ai_choice"] = "Nenhum"
    jokenpo_game_state["result_message"] = "Aguardando..."
    jokenpo_game_state["current_gesture_detected"] = "Nenhum"
    jokenpo_game_state["countdown_message"] = ""
    jokenpo_game_state["game_phase"] = "waiting_start" 
    _timer_control_start = None
    posicao_neutra_robo() # Garante mão neutra após reset
    return {"status": "success", "message": "Placar do Jokenpo resetado."}

def finish_jokenpo_round_logic():
    """Força o fim da rodada atual e volta para o estado de espera."""
    global jokenpo_game_state, _timer_control_start
    if jokenpo_game_state["game_phase"] == "round_finished":
        jokenpo_game_state["game_phase"] = "waiting_start"
        jokenpo_game_state["countdown_message"] = ""
        jokenpo_game_state["result_message"] = "Pressione 'Jogar Rodada' para começar!"
        jokenpo_game_state["player_choice"] = "Nenhum"
        jokenpo_game_state["ai_choice"] = "Nenhum"
        _timer_control_start = None
        posicao_neutra_robo() # Retorna a mão para a posição neutra
        return {"status": "success", "message": "Rodada terminada. Pronto para a próxima."}
    else:
        return {"status": "error", "message": "Nenhuma rodada para terminar no momento."}

def set_jokenpo_mediapipe_active(status):
    """Ativa ou desativa o processamento MediaPipe para o Jokenpo."""
    global jokenpo_game_state, _timer_control_start
    if status:
        jokenpo_game_state["mediapipe_processing_active"] = True
        jokenpo_game_state["game_phase"] = "waiting_start" 
        jokenpo_game_state["countdown_message"] = ""
        jokenpo_game_state["result_message"] = "Pressione 'Jogar Rodada' para começar!" 
        jokenpo_game_state["player_choice"] = "Nenhum"
        jokenpo_game_state["ai_choice"] = "Nenhum"
        _timer_control_start = None
        posicao_neutra_robo() # Garante neutra ao iniciar
        return {"status": "started", "message": "Processamento da mão Jokenpo iniciado."}
    else:
        jokenpo_game_state["mediapipe_processing_active"] = False
        jokenpo_game_state["hand_detected"] = False
        jokenpo_game_state["current_gesture_detected"] = "Nenhum"
        jokenpo_game_state["countdown_message"] = ""
        jokenpo_game_state["game_phase"] = "waiting_start" 
        jokenpo_game_state["result_message"] = "Aguardando..." 
        jokenpo_game_state["player_choice"] = "Nenhum"
        jokenpo_game_state["ai_choice"] = "Nenhum"
        _timer_control_start = None
        posicao_neutra_robo() # Garante neutra ao parar
        return {"status": "stopped", "message": "Processamento da mão Jokenpo parado."}


# --- Função Principal de Geração de Frames para Jokenpo (para uso em rota Flask) ---
def gen_jokenpo_frames(camera_index=0):
    """
    Gerador de frames de vídeo para o Jokenpo, incluindo MediaPipe, lógica de jogo
    e controle da mão robótica.
    """
    global jokenpo_game_state, _timer_control_start, _tempo_espera_countdown, _tempo_exibicao_resultado

    cap = None # Objeto da câmara

    # Print("[JOKENPO MODULE] Iniciando gerador de frames para Jokenpo...")

    # Ações iniciais ao carregar o stream:
    posicao_neutra_robo() # Garante que a mão robótica comece em posição neutra
    
    while True: # LOOP PRINCIPAL DO GERADOR DE FRAMES
        # Tenta abrir a câmera se não estiver aberta
        if cap is None or not cap.isOpened():
            # print(f"[JOKENPO MODULE] Tentando abrir a câmera (cv2.VideoCapture({camera_index}))...")
            try:
                cap = cv2.VideoCapture(int(camera_index))
                if not cap.isOpened():
                    raise IOError("Não foi possível abrir a câmera. Verifique se está em uso ou as permissões.")
                
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                # print("[JOKENPO MODULE] Câmera aberta com sucesso.")
                jokenpo_game_state["camera_is_active"] = True
            except Exception as e:
                # print(f"[JOKENPO MODULE] Erro ao iniciar a câmera: {e}. Tentando novamente em 2 segundos...")
                jokenpo_game_state["camera_is_active"] = False
                if cap: 
                    cap.release()
                cap = None 
                time.sleep(2)
                # Cria um frame de erro para exibir ao usuário
                img_error = np.zeros((480, 640, 3), dtype=np.uint8) 
                cv2.putText(img_error, "Camera Offline", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                ret, buffer = cv2.imencode('.jpg', img_error)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                continue # Continua o loop para tentar reabrir

        success, img = cap.read()
        if not success or img is None:
            # print("[JOKENPO MODULE] Erro: Não foi possível capturar a imagem da câmera ou o frame está vazio! Reabrindo...")
            if cap: cap.release() 
            cap = None 
            jokenpo_game_state["camera_is_active"] = False
            time.sleep(0.5) 
            # Cria um frame de erro para exibir ao usuário
            img_error = np.zeros((480, 640, 3), dtype=np.uint8) 
            cv2.putText(img_error, "Camera Offline", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            ret, buffer = cv2.imencode('.jpg', img_error)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            continue 

        img = cv2.flip(img, 1) # Espelha a imagem para visualização

        frameRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Reseta o estado de detecção da mão para o frame atual
        jokenpo_game_state["hand_detected"] = False
        pontos = []
        current_gesture_live_detection = "Nenhum" 

        # Somente processa MediaPipe se a flag estiver ativa
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
            
            # Atualiza o estado global com o gesto detectado em tempo real
            jokenpo_game_state["current_gesture_detected"] = current_gesture_live_detection

            # --- Lógica de Fases do Jogo ---
            if jokenpo_game_state["game_phase"] == "counting_down":
                # print(f"[JOKENPO MODULE] Game Phase: counting_down (Timer: {_timer_control_start})")
                if _timer_control_start is None: 
                    # Este bloco só deve ser executado uma vez por rodada
                    _timer_control_start = time.time()
                    jokenpo_game_state["result_message"] = "Contando..."
                    jokenpo_game_state["player_choice"] = "Nenhum" 
                    jokenpo_game_state["ai_choice"] = "Nenhum"
                    posicao_neutra_robo() # Garante mão neutra no início da contagem
                    # print(f"[JOKENPO MODULE] Contagem regressiva iniciada (Interno).")

                time_elapsed = time.time() - _timer_control_start
                segundos_restantes = int(_tempo_espera_countdown - time_elapsed) + 1

                if segundos_restantes > 0:
                    jokenpo_game_state["countdown_message"] = f"Jogue em... {segundos_restantes}"
                else:
                    # Timer de contagem regressiva zerou: Fim da jogada do jogador
                    jokenpo_game_state["countdown_message"] = "Jogada!"
                    jokenpo_game_state["game_phase"] = "round_finished" # Transição para exibir resultados
                    # print(f"[JOKENPO MODULE] Timer de jogada zerou. Fase: round_finished.")
                    
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
                    
                    # print(f"[JOKENPO MODULE] Jogador: {jokenpo_game_state['player_choice']}, IA: {jokenpo_game_state['ai_choice']}, Resultado: {result_msg}")
                    # print(f"[JOKENPO MODULE] Placar - J:{jokenpo_game_state['player_score']} | IA:{jokenpo_game_state['ai_score']} | E:{jokenpo_game_state['ties']}")
                    
                    _timer_control_start = time.time() # Reinicia timer para a duração de exibição do resultado

                    # --- COMANDO PARA O ARDUINO PARA A JOGADA DA IA ---
                    if ai_play == "Pedra":
                        fazer_pedra_robo()
                    elif ai_play == "Papel":
                        fazer_papel_robo()
                    elif ai_play == "Tesoura":
                        fazer_tesoura_robo()
                    # ---------------------------------------------------
            
            elif jokenpo_game_state["game_phase"] == "round_finished":
                # print(f"[JOKENPO MODULE] Game Phase: round_finished (Timer: {_timer_control_start})")
                jokenpo_game_state["countdown_message"] = "" 
                if _timer_control_start is not None and (time.time() - _timer_control_start) > _tempo_exibicao_resultado:
                    # Tempo de exibição esgotado, reseta para nova rodada
                    jokenpo_game_state["game_phase"] = "waiting_start"
                    jokenpo_game_state["countdown_message"] = ""
                    jokenpo_game_state["result_message"] = "Aguardando..."
                    jokenpo_game_state["player_choice"] = "Nenhum"
                    jokenpo_game_state["ai_choice"] = "Nenhum" # Reseta a jogada da IA para 'Nenhum'
                    _timer_control_start = None
                    posicao_neutra_robo() # Retorna a mão para a posição neutra
            
            elif jokenpo_game_state["game_phase"] == "waiting_start":
                # print(f"[JOKENPO MODULE] Game Phase: waiting_start")
                jokenpo_game_state["result_message"] = "Pressione 'Jogar Rodada' para começar!"
                jokenpo_game_state["countdown_message"] = ""
                jokenpo_game_state["player_choice"] = "Nenhum"
                jokenpo_game_state["ai_choice"] = "Nenhum"
                _timer_control_start = None 
                posicao_neutra_robo() # Garante neutra ao aguardar
        
        else: # MediaPipe processing is NOT active (usuário parou ou não iniciou)
            # print(f"[JOKENPO MODULE] MediaPipe inativo. Resetando estado da mão.")
            jokenpo_game_state["hand_detected"] = False
            jokenpo_game_state["current_gesture_detected"] = "Nenhum"
            jokenpo_game_state["countdown_message"] = ""
            jokenpo_game_state["game_phase"] = "waiting_start" 
            jokenpo_game_state["result_message"] = "Processamento Inativo. Ative para jogar."
            jokenpo_game_state["player_choice"] = "Nenhum"
            jokenpo_game_state["ai_choice"] = "Nenhum"
            _timer_control_start = None
            posicao_neutra_robo() # Garante neutra quando o processamento está inativo

        # --- Sobreposição de Texto no Frame OpenCV (para depuração/feedback visual) ---
        h, w, _ = img.shape
        text_y_start = h - 130 

        # Placar
        cv2.putText(img,
                    f'J:{jokenpo_game_state["player_score"]} | IA:{jokenpo_game_state["ai_score"]} | E:{jokenpo_game_state["ties"]}',
                    (int(w/2) - 130, text_y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # Mensagem de Contagem Regressiva
        if jokenpo_game_state["countdown_message"]:
            (text_width, text_height) = cv2.getTextSize(jokenpo_game_state["countdown_message"], cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            text_x = int((w - text_width) / 2)
            cv2.putText(img, jokenpo_game_state["countdown_message"],
                        (text_x, text_y_start + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

        # Mensagem de Resultado
        (result_width, result_height) = cv2.getTextSize(jokenpo_game_state["result_message"], cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        result_x = int((w - result_width) / 2)

        cor_resultado = (150, 0, 255) # Púrpura padrão
        if "Voce venceu!" in jokenpo_game_state["result_message"]:
            cor_resultado = (0, 255, 0) # Verde
        elif "Robo venceu!" in jokenpo_game_state["result_message"]:
            cor_resultado = (0, 0, 255) # Vermelho
        elif "Empate!" in jokenpo_game_state["result_message"]:
            cor_resultado = (255, 255, 0) # Ciano

        cv2.putText(img, jokenpo_game_state["result_message"],
                    (result_x, text_y_start + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, cor_resultado, 2)

        # Gesto do Jogador
        cv2.putText(img, f'Sua jogada: {jokenpo_game_state["current_gesture_detected"]}',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        # Jogada da IA
        ai_display_choice = jokenpo_game_state["ai_choice"] if jokenpo_game_state["game_phase"] == "round_finished" else "..."
        cv2.putText(img, f'Jogada IA: {ai_display_choice}',
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        # Converte o frame OpenCV para o formato JPEG e o cede (yield) para o stream HTTP
        ret, buffer = cv2.imencode('.jpg', img)
        if not ret:
            # print("[JOKENPO MODULE] Erro: Falha ao codificar o frame para JPEG! Pode ser um frame vazio ou problema de dados.")
            continue # Pula a iteração atual se a codificação falhar

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # Não precisa de time.sleep aqui, o Flask já controla a taxa da resposta.
        # time.sleep(0.01) 

    if cap: # Garante que 'cap' existe antes de liberar
        cap.release()
    # print("[JOKENPO MODULE] Gerador de frames para Jokenpo finalizado.")

