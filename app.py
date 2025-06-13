from flask import Flask, render_template, Response, jsonify
from src.arduino import gen_arduino_frames
from src.lousa import gen_frames


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/lousa')
def lousa():
    return render_template('lousa.html')

@app.route('/video_arduino')
def video_arduino():
    return Response(gen_arduino_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/arduino')
def arduino():
    return render_template('arduino.html')

@app.route('/conteudo/<int:id>')
def conteudo(id):
    # Conteúdo fake para outros quadros
    return jsonify({'conteudo': f'Você clicou no quadro {id}.'})

if __name__ == '__main__':
    app.run(debug=True)
