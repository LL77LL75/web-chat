from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import os, json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
socketio = SocketIO(app, cors_allowed_origins="*")

# File paths
USERNAMES_FILE = "usernames.txt"
PASSWORDS_FILE = "passwords.txt"
RANKS_FILE = "ranks.txt"
ROOMS_FILE = "rooms.json"

# ----------------- User Management -----------------
def load_users():
    with open(USERNAMES_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def load_passwords():
    with open(PASSWORDS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def load_ranks():
    with open(RANKS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def load_rooms():
    if os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_rooms(rooms):
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f)

# ----------------- API Routes -----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data.get("username"), data.get("password")

    users, passwords, ranks = load_users(), load_passwords(), load_ranks()
    if username in users:
        idx = users.index(username)
        if password == passwords[idx]:
            return jsonify({"status": "success", "rank": ranks[idx]})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/rooms", methods=["GET"])
def get_rooms():
    return jsonify(load_rooms())

@app.route("/create_room", methods=["POST"])
def create_room():
    data = request.json
    code = data.get("code")
    user = data.get("user")
    rooms = load_rooms()
    if code in rooms:
        return jsonify({"status": "error", "message": "Room already exists"}), 400
    rooms[code] = {"hosts": [user], "members": [], "bans": {"users": [], "by": []}, "mutes": {"users": [], "by": []}}
    save_rooms(rooms)
    return jsonify({"status": "success", "room": rooms[code]})

@app.route("/shutdown_room", methods=["POST"])
def shutdown_room():
    data = request.json
    code = data.get("code")
    rooms = load_rooms()
    if code not in rooms:
        return jsonify({"status": "error", "message": "Room not found"}), 404
    del rooms[code]
    save_rooms(rooms)
    return jsonify({"status": "success"})

# ----------------- Socket.IO Events -----------------
@socketio.on("join")
def handle_join(data):
    username, room = data["username"], data["room"]
    join_room(room)
    rooms = load_rooms()
    if room in rooms:
        rooms[room]["members"].append(username)
        save_rooms(rooms)
    emit("message", {"user": "Server", "msg": f"{username} joined the room"}, room=room)

@socketio.on("leave")
def handle_leave(data):
    username, room = data["username"], data["room"]
    leave_room(room)
    rooms = load_rooms()
    if room in rooms and username in rooms[room]["members"]:
        rooms[room]["members"].remove(username)
        save_rooms(rooms)
    emit("message", {"user": "Server", "msg": f"{username} left the room"}, room=room)

@socketio.on("chat")
def handle_chat(data):
    emit("message", {"user": data["username"], "msg": data["msg"]}, room=data["room"])

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
