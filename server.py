from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from database import make_room, addToRoom

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

@app.route("/make-room")
def room_maker():
    return render_template("for_room_making.html")


@socketio.on("create_room")
def handle_create_room(data):
    """
    Client emits: socket.emit("create_room", { name: "Cool Room" });
    """
    name = data.get("name")
    host_id = request.sid  # socket.io session id

    room_id, data = make_room(name, host_id)

    print(data)

    if room_id: 
        emit("room_created", {
            "success": True,
            "room_id": room_id,
            "name": name,
            "host_id": host_id
        }, room=request.sid)  # only send back to the creator
    else:
        emit("room_created", {
            "success": False,
            "error": "Room creation failed"
        }, room=request.sid)

@socketio.on("join_room")
def join_user_to_room(data):
    """
    Client emits: socket.emit("create_room", { name: "Cool Room" });
    """
    name = data.get("name")
    room_name = data.get("room")
    user_id = request.sid  # socket.io session id

    name, room = addToRoom(name, user_id, room_name)

    data = {'name': name, 'room': room}

    print(data)

    if name: 
        emit("added_to_room", {
            "success": True,
            "room_id": room,
            "name": name,
            "host_id": user_id
        }, room=request.sid)  # only send back to the creator
    else:
        if room:
            err = room
        else:
            err =  "Room joining failed"
        emit("added_to_room", {
            "success": False,
            "error": err
        }, room=request.sid)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host="0.0.0.0")
