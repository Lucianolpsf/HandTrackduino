from flask import Flask, render_template, Response, jsonify, request
from src.robo.servo_braco3d import rotina_automatica
from services.cameras.camera import listar_cameras_disponiveis
from services.cameras.camera_manager import CameraManager
from services.github import get_cards
from src.robo.arduino import gen_arduino_frames
from src.desenho.lousa import gen_lousa_frames
import serial.tools.list_ports
import sys


app = Flask(__name__)

camera_index_global = 0  # Valor padrão
arduino_port_global = None

@app.route('/')
def index():
    visoes = ['Robô', 'Desenho']
    cards_data = get_cards()
    return render_template('index.html', visoes=visoes, cards=cards_data)


@app.route('/lousa')
def lousa():
    return render_template('lousa.html')


@app.route('/arduino')
def arduino():
    return render_template('arduino.html')


@app.route("/cameras")
def cameras():
    lista = listar_cameras_disponiveis()
    return jsonify(lista)


@app.route("/set_camera", methods=["POST"])
def set_camera():
    data = request.get_json()
    index = int(data.get("camera_index", 0))
    CameraManager.get_instance().set_camera(index)
    return jsonify({"status": "ok", "camera_index": index})


@app.route("/release_camera", methods=["POST"])
def release_camera():
    CameraManager.get_instance().release()
    return jsonify({"status": "released"})


@app.route('/video_lousa')
def video_lousa():
    return Response(gen_lousa_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_arduino')
def video_arduino():
    return Response(gen_arduino_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/cards_json')
def cards_json():
    cards_data = get_cards()
    return jsonify(cards_data)


@app.route("/arduino_automatico")
def arduino_automatico():
    estado = request.args.get("estado", "off")
    rotina_automatica(on=(estado == "on"))
    return f"Modo automático {'ativado' if estado == 'on' else 'desativado'}"


@app.route("/arduino_ports")
def arduino_ports():
    ports = []
    for port in serial.tools.list_ports.comports():
        desc = (port.description or "").lower()
        manuf = (port.manufacturer or "").lower() if port.manufacturer else ""
        device = port.device.lower()
        # Filtros comuns para placas Arduino e clones
        is_arduino = (
            "arduino" in desc or
            "arduino" in manuf or
            "ch340" in desc or
            "wchusb" in desc or
            "usb serial" in desc or
            "acm" in device or
            "usb" in device or
            "serial" in desc
        )
        # No Windows, portas COMx geralmente são Arduino/clones
        is_windows_com = sys.platform.startswith("win") and device.startswith("com")
        if is_arduino or is_windows_com:
            ports.append(port.device)
    # Se não encontrou nenhuma, mostra todas para debug
    if not ports:
        ports = [port.device for port in serial.tools.list_ports.comports()]
    return jsonify(ports)


@app.route("/set_arduino_port", methods=["POST"])
def set_arduino_port():
    global arduino_port_global
    data = request.get_json()
    arduino_port_global = data.get("port")
    return jsonify({"status": f"Porta {arduino_port_global} selecionada!"})


@app.route("/get_arduino_port")
def get_arduino_port():
    global arduino_port_global
    return jsonify({"port": arduino_port_global})


if __name__ == '__main__':
    app.run(debug=True)
