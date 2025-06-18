from flask import Flask, render_template, Response, jsonify, request
from src.jokenpo.jokenpo import (
    gen_jokenpo_frames, 
    get_jokenpo_game_state_data, 
    start_jokenpo_round_logic, 
    reset_jokenpo_score_logic, 
    finish_jokenpo_round_logic,
    set_jokenpo_mediapipe_active # Para controlar o MediaPipe do Jokenpo
)
from src.robo.servo_braco3d import rotina_automatica 
from services.cameras.camera import listar_cameras_disponiveis
from services.github import get_cards
from src.robo.arduino import gen_arduino_frames 
from src.desenho.lousa import gen_frames       


app = Flask(__name__)


@app.route('/')
def index():
    visoes = ['Robô', 'Desenho', 'Jokenpo']
    cards_data = get_cards()
    return render_template('index.html', visoes=visoes, cards=cards_data)


@app.route('/lousa')
def lousa():
    return render_template('lousa.html')

@app.route('/jokenpo')
def jokenpo_page(): 
    return render_template('jokenpo.html')


@app.route('/arduino')
def arduino():
    return render_template('arduino.html')


@app.route("/cameras")
def cameras():
    lista = listar_cameras_disponiveis()
    return jsonify(lista)


@app.route('/cards_json')
def cards_json():
    cards_data = get_cards()
    return jsonify(cards_data)


@app.route("/arduino_automatico")
def arduino_automatico():
    estado = request.args.get("estado", "off")
    rotina_automatica(on=(estado == "on"))
    return f"Modo automático {'ativado' if estado == 'on' else 'desativado'}"


@app.route('/video_lousa/<int:camera_index>')
def video_lousa(camera_index):
    return Response(gen_frames(camera_index),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_arduino/<int:camera_index>')
def video_arduino(camera_index):
    return Response(gen_arduino_frames(camera_index),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_jokenpo/<int:camera_index>')
def video_jokenpo(camera_index):
    return Response(gen_jokenpo_frames(camera_index),mimetype='multipart/x-mixed-replace; boundary=frame')

# --- Rotas de Controle de Estado do Jokenpo (movidas para app.py) ---

@app.route('/jokenpo_game_status')
def jokenpo_status():
    """Endpoint para retornar o estado atual do jogo de Jokenpo como JSON."""
    return jsonify(get_jokenpo_game_state_data())

@app.route('/play_jokenpo')
def play_jokenpo():
    """
    Endpoint para iniciar uma rodada de Jokenpo.
    A lógica de iniciar a contagem regressiva é delegada ao módulo jokenpo.
    """
    response_data = start_jokenpo_round_logic()
    return jsonify(response_data)

@app.route('/reset_jokenpo')
def reset_jokenpo():
    """Endpoint para resetar o placar do Jokenpo."""
    response_data = reset_jokenpo_score_logic()
    return jsonify(response_data)

@app.route('/finish_round') 
def finish_round():
    """Endpoint para terminar a rodada atual e voltar para o estado de espera."""
    response_data = finish_jokenpo_round_logic()
    return jsonify(response_data)

@app.route('/control_processing/<action>')
def control_processing(action):
    """
    Endpoint para controlar se o processamento MediaPipe do Jokenpo está ativo ou não.
    """
    if action == "start":
        response_data = set_jokenpo_mediapipe_active(True)
    elif action == "stop":
        response_data = set_jokenpo_mediapipe_active(False)
    else:
        response_data = {"status": "invalid_action", "message": "Ação inválida."}
    return jsonify(response_data)


if __name__ == '__main__':
        app.run(debug=True) 