from flask import Flask, render_template, Response, jsonify, request
from src.jokenpo.jokenpo import gen_jokenpo_frames
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
def jokenpo():
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

if __name__ == '__main__':
    app.run(debug=True)
