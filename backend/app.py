from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import os, json, time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
socketio = SocketIO(app, cors_allowed_origins="*")

USERNAMES_FILE = "usernames.txt"
PASSWORDS_FILE = "passwords.txt"
RANKS_FILE = "ranks.txt"
ROOMS_FILE = "rooms.json"

# -------- Utilities --------
def load_users(): return [line.strip() for line in open(USERNAMES_FILE)]
def load_passwords(): return [line.strip() for line in open(PASSWORDS_FILE)]
def load_ranks(): return [line.strip() for line in open(RANKS_FILE)]

def load_rooms():
    if os.path.exists(ROOMS_FILE):
        return json.load(open(ROOMS_FILE))
    return {}

def save_rooms(rooms): json.dump(rooms, open(ROOMS_FILE, "w"))

def is_admin(username):
    users, ranks = load_users(), load_ranks()
    if username in users:
        idx = users.index(username)
        return ranks[idx] in ["admin", "core"]
    return False

def timestamp(): return time.strftime("%I:%M %p")

# -------- API --------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data.get("username"), data.get("password")
    users, pwds, ranks = load_users(), load_passwords(), load_ranks()
    if username in users:
        idx = users.index(username)
        if pwds[idx] == password:
            return jsonify({"status": "success", "rank": ranks[idx]})
    return jsonify({"status": "error"}), 401

@app.route("/rooms", methods=["GET"])
def get_rooms(): return jsonify(load_rooms())

@app.route("/create_room", methods=["POST"])
def create_room():
    data = request.json
    code, user = data.get("code"), data.get("user")
    rooms = load_rooms()
    if code in rooms:
        return jsonify({"status": "exists", "room": rooms[code]}), 200
    rooms[code] = {
        "hosts": [user],
        "members": [],
        "bans": {"users": [], "by": [], "levels": []},
        "mutes": {"users": [], "by": [], "levels": []},
        "messages": []
    }
    save_rooms(rooms)
    return jsonify({"status": "created", "room": rooms[code]})

@app.route("/shutdown_room", methods=["POST"])
def shutdown_room():
    code = request.json.get("code")
    rooms = load_rooms()
    if code not in rooms:
        return jsonify({"status": "error"}), 404
    del rooms[code]
    save_rooms(rooms)
    return jsonify({"status": "success"})

# -------- Socket.IO --------
@socketio.on("join")
def join(data):
    user, room = data["username"], data["room"]
    join_room(room)
    rooms = load_rooms()
    if room in rooms:
        if user not in rooms[room]["members"]:
            rooms[room]["members"].append(user)
        save_rooms(rooms)
        # send chat history
        emit("history", rooms[room]["messages"], to=request.sid)
    emit("message", {"id": str(time.time()), "user": "Server", "msg": f"{user} joined", "time": timestamp()}, room=room)

@socketio.on("leave")
def leave(data):
    user, room = data["username"], data["room"]
    leave_room(room)
    rooms = load_rooms()
    if room in rooms and user in rooms[room]["members"]:
        rooms[room]["members"].remove(user)
        save_rooms(rooms)
    emit("message", {"id": str(time.time()), "user": "Server", "msg": f"{user} left", "time": timestamp()}, room=room)

@socketio.on("chat")
def chat(data):
    user, room, msg = data["username"], data["room"], data["msg"]
    rooms = load_rooms()

    if msg.startswith("?/"):
        handle_command(user, room, msg)
        return

    # save message
    new_msg = {
        "id": str(time.time()),  # unique id
        "user": user,
        "msg": msg,
        "time": timestamp(),
        "edited": False,
        "edited_time": None
    }
    rooms[room]["messages"].append(new_msg)
    save_rooms(rooms)

    emit("message", new_msg, room=room)

@socketio.on("delete_message")
def delete_message(data):
    user, room, msg_id = data["username"], data["room"], data["id"]
    rooms = load_rooms()
    if room in rooms:
        for m in rooms[room]["messages"]:
            if m["id"] == msg_id and m["user"] == user:  # only author can delete
                rooms[room]["messages"].remove(m)
                save_rooms(rooms)
                emit("delete", {"id": msg_id}, room=room)
                break

@socketio.on("edit_message")
def edit_message(data):
    user, room, msg_id, new_text = data["username"], data["room"], data["id"], data["new"]
    rooms = load_rooms()
    if room in rooms:
        for m in rooms[room]["messages"]:
            if m["id"] == msg_id and m["user"] == user:  # only author can edit
                m["msg"] = new_text
                m["edited"] = True
                m["edited_time"] = timestamp()
                save_rooms(rooms)
                emit("edit", m, room=room)
                break

# -------- Command Handling --------
def handle_command(user, room, msg):
    # keep your previous command handling logic (ban, mute, kick, etc.)
    pass

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
