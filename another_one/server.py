from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit
import os, json, uuid

# ----------------------------
# Encoding / Decoding (kept from your logic mapping)
# ----------------------------
c2n = {**{chr(i + 96): i for i in range(1, 27)}, " ": 27, ",": 28, ".": 29, "!": 30, "/": 31}
n2c = {v: k for k, v in c2n.items()}

def enc(t):
    # kept for compatibility, but we send plaintext over websockets in this web version
    import random
    return [
        [
            int((b[i:i + (gval_inner := random.choice([2, 3]))]).ljust(gval_inner, "0"), 2)
            for gval in [gval_inner]  # choose gval for this character
            for b in [bin(c2n[ch])[2:]]       # assign b for this character
            for i in range(0, len(b), gval)
        ]
        for ch in t.lower()
    ]

def dec(d):
    return "".join(
        n2c[int("".join(bin(g)[2:].zfill(2 if g < 4 else 3) for g in grp).lstrip("0") or "0", 2)]
        for grp in d
    )

# ----------------------------
# Files and helpers
# ----------------------------
USERNAMES_FILE = "usernames.txt"
PASSWORDS_FILE = "passwords.txt"
RANKS_FILE = "ranks.txt"
ROOMS_FILE = "rooms.json"

def ensure_files():
    # create simple default files if not present
    if not os.path.exists(USERNAMES_FILE):
        with open(USERNAMES_FILE, "w") as f:
            f.write("admin\n")
    if not os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, "w") as f:
            f.write("admin\n")
    if not os.path.exists(RANKS_FILE):
        with open(RANKS_FILE, "w") as f:
            f.write("core\n")
    if not os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, "w") as f:
            json.dump({}, f)

def load_users():
    with open(USERNAMES_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_passwords():
    with open(PASSWORDS_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_ranks():
    with open(RANKS_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_users_passwords_ranks(users, passwords, ranks):
    with open(USERNAMES_FILE, "w") as f:
        f.writelines([f"{u}\n" for u in users])
    with open(PASSWORDS_FILE, "w") as f:
        f.writelines([f"{p}\n" for p in passwords])
    with open(RANKS_FILE, "w") as f:
        f.writelines([f"{r}\n" for r in ranks])

def load_rooms():
    if os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_rooms(rooms):
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f, indent=2)

# ----------------------------
# Simple token session store (in-memory)
# ----------------------------
sessions = {}  # token -> {username, rank}

# ----------------------------
# Flask + SocketIO
# ----------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

ensure_files()

# ----------------------------
# Routes: render UI / api
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    users = load_users()
    passwords = load_passwords()
    ranks = load_ranks()

    if username not in users:
        return jsonify({"success": False, "message": "Username not found."}), 404

    idx = users.index(username)
    if password != passwords[idx]:
        return jsonify({"success": False, "message": "Incorrect password."}), 401

    rank = ranks[idx]
    token = str(uuid.uuid4())
    sessions[token] = {"username": username, "rank": rank}
    return jsonify({"success": True, "token": token, "username": username, "rank": rank})

@app.route("/api/change_credentials", methods=["POST"])
def api_change_credentials():
    data = request.get_json() or {}
    token = data.get("token")
    new_username = data.get("new_username", "").strip()
    new_password = data.get("new_password", "").strip()

    if token not in sessions:
        return jsonify({"success": False, "message": "Invalid token."}), 401
    current = sessions[token]["username"]

    users = load_users()
    passwords = load_passwords()
    ranks = load_ranks()

    if current not in users:
        return jsonify({"success": False, "message": "User not found."}), 404

    idx = users.index(current)
    users[idx] = new_username or current
    passwords[idx] = new_password or passwords[idx]

    save_users_passwords_ranks(users, passwords, ranks)

    # update session username
    sessions[token]["username"] = users[idx]

    return jsonify({"success": True, "message": "Credentials updated.", "username": users[idx]})

@app.route("/api/rooms", methods=["GET"])
def api_list_rooms():
    rooms = load_rooms()
    summary = {}
    for code, details in rooms.items():
        summary[code] = {
            "hosts": details.get("hosts", []),
            "members": details.get("members", [])
        }
    return jsonify({"success": True, "rooms": summary})

@app.route("/api/create_room", methods=["POST"])
def api_create_room():
    data = request.get_json() or {}
    token = data.get("token")
    code = data.get("code", "").strip()

    if token not in sessions:
        return jsonify({"success": False, "message": "Invalid token."}), 401
    if not code:
        return jsonify({"success": False, "message": "Room code required."}), 400

    rooms = load_rooms()
    if code in rooms:
        return jsonify({"success": False, "message": "Room already exists."}), 400

    rooms[code] = {"hosts": [], "members": [], "bans": {"users": [], "by": []}, "mutes": {"users": [], "by": []}}
    save_rooms(rooms)
    return jsonify({"success": True, "room": rooms[code]})

# admin promote (simple)
@app.route("/api/promote", methods=["POST"])
def api_promote():
    data = request.get_json() or {}
    token = data.get("token")
    username_to_promote = data.get("username")

    if token not in sessions:
        return jsonify({"success": False, "message": "Invalid token."}), 401
    actor = sessions[token]
    if actor["rank"] != "core":
        return jsonify({"success": False, "message": "Not authorized."}), 403

    users = load_users()
    ranks = load_ranks()
    if username_to_promote not in users:
        return jsonify({"success": False, "message": "User not found."}), 404
    idx = users.index(username_to_promote)
    ranks[idx] = "core"
    with open(RANKS_FILE, "w") as f:
        f.writelines([f"{r}\n" for r in ranks])
    return jsonify({"success": True, "message": f"{username_to_promote} promoted to core."})

# ----------------------------
# SocketIO events (chat)
# ----------------------------
@socketio.on("connect")
def on_connect():
    emit("server_msg", {"msg": "Connected to chat server."})

@socketio.on("join")
def on_join(data):
    token = data.get("token")
    room = data.get("room")
    if token not in sessions:
        emit("join_response", {"success": False, "message": "Invalid token."})
        return
    username = sessions[token]["username"]
    rooms = load_rooms()
    if room not in rooms:
        emit("join_response", {"success": False, "message": "Room not found."})
        return

    # check ban
    if username in rooms[room].get("bans", {}).get("users", []):
        emit("join_response", {"success": False, "message": "You are banned from this room."})
        return

    join_room(room)
    # update rooms data
    if username not in rooms[room]["members"]:
        rooms[room]["members"].append(username)
    save_rooms(rooms)

    emit("join_response", {"success": True, "room": room, "username": username})
    emit("system", {"msg": f"{username} has joined the room."}, room=room)

@socketio.on("leave")
def on_leave(data):
    token = data.get("token")
    room = data.get("room")
    if token not in sessions:
        return
    username = sessions[token]["username"]
    leave_room(room)
    rooms = load_rooms()
    if room in rooms and username in rooms[room].get("members", []):
        rooms[room]["members"].remove(username)
        save_rooms(rooms)
    emit("system", {"msg": f"{username} has left the room."}, room=room)

@socketio.on("message")
def on_message(data):
    token = data.get("token")
    room = data.get("room")
    text = data.get("text", "")
    if token not in sessions:
        emit("message_response", {"success": False, "message": "Invalid token."})
        return
    username = sessions[token]["username"]
    rooms = load_rooms()
    # check mute
    if username in rooms.get(room, {}).get("mutes", {}).get("users", []):
        emit("message_response", {"success": False, "message": "You are muted in this room."})
        return

    # echo to room
    emit("chat", {"username": username, "text": text}, room=room)
    emit("message_response", {"success": True})

@socketio.on("disconnect")
def on_disconnect():
    # nothing fancy here
    pass

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    print("Starting HTTP+SocketIO server on http://0.0.0.0:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
