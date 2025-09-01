from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def home():
    return render_template("index.html")

# handle chat messages
@socketio.on("message")
def handle_message(msg):
    if msg:
        payload = {"sid": request.sid, "msg": msg}
        send(payload, broadcast=True)

# custom event example (drawing data)
@socketio.on("draw_event")
def handle_draw(data):
    print("Draw:", data)
    emit("draw_event", data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host="0.0.0.0")
