# backend/app.py
# Flask + SocketIO backend using rooms.json and plaintext username/password files.
# Provides:
#  - /login, /rooms, /create_room, /shutdown_room, /room_members APIs
#  - Websocket events: join, leave, chat
#  - commands (?/ban, ?/unban, ?/mute, ?/unmute, ?/kick, ?/msg, ?/rank)

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import os, json, threading

BASE_DIR = os.path.dirname(__file__) or "."
USERNAMES_FILE = os.path.join(BASE_DIR, "usernames.txt")
PASSWORDS_FILE = os.path.join(BASE_DIR, "passwords.txt")
RANKS_FILE = os.path.join(BASE_DIR, "ranks.txt")
ROOMS_FILE = os.path.join(BASE_DIR, "rooms.json")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace_this_with_a_real_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# mapping username -> set of socket session ids
connected = {}  # username -> set([sid, ...])
connected_lock = threading.Lock()

# helpers for file operations
def load_users():
    if not os.path.exists(USERNAMES_FILE):
        return []
    with open(USERNAMES_FILE, "r") as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def load_passwords():
    if not os.path.exists(PASSWORDS_FILE):
        return []
    with open(PASSWORDS_FILE, "r") as f:
        return [l.strip() for l in f.readlines()]

def load_ranks():
    if not os.path.exists(RANKS_FILE):
        return []
    with open(RANKS_FILE, "r") as f:
        return [l.strip() for l in f.readlines()]

def save_ranks(ranks_list):
    with open(RANKS_FILE, "w") as f:
        f.writelines([f"{r}\n" for r in ranks_list])

def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return {}
    with open(ROOMS_FILE, "r") as f:
        return json.load(f)

def save_rooms(data):
    with open(ROOMS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(username):
    users = load_users()
    ranks = load_ranks()
    if username in users:
        idx = users.index(username)
        r = ranks[idx] if idx < len(ranks) else ""
        return r.lower() in ("admin", "core")
    return False

def get_user_rank(username):
    users = load_users()
    ranks = load_ranks()
    if username in users:
        idx = users.index(username)
        return ranks[idx] if idx < len(ranks) else "member"
    return "member"

# ensure rooms.json exists
if not os.path.exists(ROOMS_FILE):
    save_rooms({})

# -----------------------
# HTTP API endpoints
# -----------------------
@app.route("/login", methods=["POST"])
def api_login():
    d = request.json or {}
    username = (d.get("username") or "").strip()
    password = (d.get("password") or "").strip()

    users = load_users()
    passwords = load_passwords()
    ranks = load_ranks()

    if username in users:
        i = users.index(username)
        if i < len(passwords) and passwords[i] == password:
            return jsonify({"status":"success", "rank": ranks[i] if i < len(ranks) else "member"})
    return jsonify({"status":"error","message":"Invalid credentials"}), 401

@app.route("/rooms", methods=["GET"])
def api_rooms():
    rooms = load_rooms()
    return jsonify(rooms)

@app.route("/create_room", methods=["POST"])
def api_create_room():
    d = request.json or {}
    code = (d.get("code") or "").strip()
    user = (d.get("user") or "").strip()
    if not code:
        return jsonify({"status":"error","message":"code required"}), 400
    rooms = load_rooms()
    if code in rooms:
        return jsonify({"status":"exists","room":rooms[code]}), 200
    rooms[code] = {
        "hosts": [user],
        "members": [],
        "bans": {"users": [], "by": [], "levels": []},
        "mutes": {"users": [], "by": [], "levels": []}
    }
    save_rooms(rooms)
    return jsonify({"status":"created","room":rooms[code]}), 201

@app.route("/shutdown_room", methods=["POST"])
def api_shutdown_room():
    d = request.json or {}
    code = (d.get("code") or "").strip()
    if not code:
        return jsonify({"status":"error","message":"code required"}), 400
    rooms = load_rooms()
    if code not in rooms:
        return jsonify({"status":"error","message":"room not found"}), 404
    del rooms[code]
    save_rooms(rooms)
    return jsonify({"status":"success"}), 200

@app.route("/room_members", methods=["POST"])
def api_room_members():
    d = request.json or {}
    code = (d.get("code") or "").strip()
    if not code:
        return jsonify({"status":"error","message":"code required"}), 400
    rooms = load_rooms()
    if code not in rooms:
        return jsonify({"status":"error","message":"room not found"}), 404
    room = rooms[code]
    # Build members list and annotate mutes/bans with levels
    members = []
    for m in room.get("members", []):
        entry = {"name": m}
        # check ban
        if m in room.get("bans", {}).get("users", []):
            idx = room["bans"]["users"].index(m)
            lvl = room["bans"]["levels"][idx] if idx < len(room["bans"]["levels"]) else 1
            entry["banned"] = True
            entry["ban_level"] = lvl
        # check mute
        if m in room.get("mutes", {}).get("users", []):
            idx2 = room["mutes"]["users"].index(m)
            lvl2 = room["mutes"]["levels"][idx2] if idx2 < len(room["mutes"]["levels"]) else 1
            entry["muted"] = True
            entry["mute_level"] = lvl2
        members.append(entry)
    return jsonify({"status":"success","members":members,"room":room})

# -----------------------
# SocketIO: connections & chat & commands
# -----------------------
@socketio.on("connect")
def on_connect():
    # no auth at connect; frontend will emit 'identify' with username after connecting
    emit("sys", {"msg":"connected"})

@socketio.on("identify")
def on_identify(data):
    username = (data.get("username") or "").strip()
    sid = request.sid
    if not username:
        return
    with connected_lock:
        connected.setdefault(username, set()).add(sid)
    # attach username on session (SocketIO supports storing via environ)
    # but we'll just keep mapping; send ack
    emit("identified", {"ok": True, "username": username})

@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    # remove sid from all usernames
    with connected_lock:
        to_remove = []
        for uname, sids in list(connected.items()):
            if sid in sids:
                sids.remove(sid)
            if not sids:
                to_remove.append(uname)
        for u in to_remove:
            connected.pop(u, None)

@socketio.on("join")
def on_join(data):
    username = (data.get("username") or "").strip()
    room = (data.get("room") or "").strip()
    if not username or not room:
        emit("sys", {"msg":"missing username or room"})
        return

    rooms = load_rooms()
    if room not in rooms:
        emit("join_response", {"success": False, "message": "room not found"})
        return

    # check ban
    if username in rooms[room].get("bans", {}).get("users", []):
        idx = rooms[room]["bans"]["users"].index(username)
        level = rooms[room]["bans"]["levels"][idx] if idx < len(rooms[room]["bans"]["levels"]) else 1
        emit("join_response", {"success": False, "message": f"you are banned (level {level})"})
        return

    join_room(room)
    if username not in rooms[room]["members"]:
        rooms[room]["members"].append(username)
        save_rooms(rooms)

    emit("join_response", {"success": True, "room": room})
    socketio.emit("message", {"user":"Server", "msg": f"{username} joined the room."}, room=room)

@socketio.on("leave")
def on_leave(data):
    username = (data.get("username") or "").strip()
    room = (data.get("room") or "").strip()
    if not username or not room:
        return
    leave_room(room)
    rooms = load_rooms()
    if room in rooms and username in rooms[room]["members"]:
        rooms[room]["members"].remove(username)
        save_rooms(rooms)
    socketio.emit("message", {"user":"Server", "msg": f"{username} left the room."}, room=room)

@socketio.on("chat")
def on_chat(data):
    username = (data.get("username") or "").strip()
    room = (data.get("room") or "").strip()
    msg = data.get("msg") or ""
    if msg.startswith("?/"):
        handle_command(username, room, msg)
        return
    # check mute
    rooms = load_rooms()
    if room in rooms and username in rooms[room].get("mutes", {}).get("users", []):
        # you are muted: ignore message and send notice
        emit("message", {"user":"Server","msg": f"{username}, you are muted and cannot send messages."})
        return
    socketio.emit("message", {"user": username, "msg": msg}, room=room)

# -----------------------
# Command handling
# -----------------------
def handle_command(actor, room, msg):
    """
    Commands start with '?/' followed by:
    ban name level
    unban name
    mute name level
    unmute name
    kick name
    msg name (message in parentheses)  -> syntax: ?/msg banana (hello there)
    rank name rank
    """
    parts = msg[2:].strip().split()
    if not parts:
        return
    cmd = parts[0].lower()
    args = parts[1:]

    rooms = load_rooms()
    if room not in rooms:
        emit("message", {"user":"Server", "msg":"Room not found."})
        return

    def send_room(text):
        socketio.emit("message", {"user":"Server", "msg": text}, room=room)

    actor_is_admin = is_admin(actor)

    try:
        if cmd == "ban" and actor_is_admin:
            if len(args) != 2:
                send_room("Usage: ?/ban [name] [level]")
                return
            target, level_s = args[0], args[1]
            level = int(level_s)
            if target not in rooms[room]["members"]:
                send_room(f"{target} is not in the room.")
                return
            # add ban entry (allow duplicates? avoid duplicate target)
            if target in rooms[room]["bans"]["users"]:
                idx = rooms[room]["bans"]["users"].index(target)
                rooms[room]["bans"]["levels"][idx] = level
                rooms[room]["bans"]["by"][idx] = actor
            else:
                rooms[room]["bans"]["users"].append(target)
                rooms[room]["bans"]["by"].append(actor)
                rooms[room]["bans"]["levels"].append(level)
            # if target is in members, remove
            if target in rooms[room]["members"]:
                rooms[room]["members"].remove(target)
            save_rooms(rooms)
            send_room(f"{target} banned (level {level})")
            # notify target if connected and force them to leave the room client-side
            notify_user(target, {"type":"banned","room":room,"level":level})

        elif cmd == "unban" and actor_is_admin:
            if len(args) != 1:
                send_room("Usage: ?/unban [name]")
                return
            target = args[0]
            if target in rooms[room]["bans"]["users"]:
                idx = rooms[room]["bans"]["users"].index(target)
                for k in ["users","by","levels"]:
                    try:
                        rooms[room]["bans"][k].pop(idx)
                    except Exception:
                        pass
                save_rooms(rooms)
                send_room(f"{target} unbanned")
            else:
                send_room(f"{target} not banned")

        elif cmd == "mute" and actor_is_admin:
            if len(args) != 2:
                send_room("Usage: ?/mute [name] [level]")
                return
            target, level_s = args[0], args[1]
            level = int(level_s)
            if target in rooms[room]["mutes"]["users"]:
                idx = rooms[room]["mutes"]["users"].index(target)
                rooms[room]["mutes"]["levels"][idx] = level
                rooms[room]["mutes"]["by"][idx] = actor
            else:
                rooms[room]["mutes"]["users"].append(target)
                rooms[room]["mutes"]["by"].append(actor)
                rooms[room]["mutes"]["levels"].append(level)
            save_rooms(rooms)
            send_room(f"{target} muted (level {level})")
            notify_user(target, {"type":"muted","room":room,"level":level})

        elif cmd == "unmute" and actor_is_admin:
            if len(args) != 1:
                send_room("Usage: ?/unmute [name]")
                return
            target = args[0]
            if target in rooms[room]["mutes"]["users"]:
                idx = rooms[room]["mutes"]["users"].index(target)
                for k in ["users","by","levels"]:
                    try:
                        rooms[room]["mutes"][k].pop(idx)
                    except Exception:
                        pass
                save_rooms(rooms)
                send_room(f"{target} unmuted")
            else:
                send_room(f"{target} not muted")

        elif cmd == "kick" and actor_is_admin:
            if len(args) != 1:
                send_room("Usage: ?/kick [name]")
                return
            target = args[0]
            if target in rooms[room]["members"]:
                rooms[room]["members"].remove(target)
                save_rooms(rooms)
                send_room(f"{target} kicked from room")
                notify_user(target, {"type":"kicked","room":room})
            else:
                send_room(f"{target} not in room")

        elif cmd == "msg":
            # format: ?/msg name (message text)  OR ?/msg name message...
            if len(args) < 2:
                send_room("Usage: ?/msg [name] (message)")
                return
            target = args[0]
            # extract message inside parentheses if present
            rest = msg[msg.find(target) + len(target):].strip()
            message = ""
            if rest.startswith("(") and ")" in rest:
                message = rest[1:rest.find(")")]
            else:
                message = " ".join(args[1:])
            # send privately to target if connected
            if target in connected:
                notify_user(target, {"type":"private","from":actor,"message":message})
                # also confirm to actor
                notify_user(actor, {"type":"private-sent","to":target,"message":message})
            else:
                notify_user(actor, {"type":"private-failed","to":target,"message":"user not online"})

        elif cmd == "rank" and actor_is_admin:
            if len(args) != 2:
                send_room("Usage: ?/rank [name] [rank]")
                return
            target, newrank = args[0], args[1]
            users = load_users()
            ranks = load_ranks()
            if target in users:
                idx = users.index(target)
                if idx < len(ranks):
                    ranks[idx] = newrank
                else:
                    # pad
                    while len(ranks) < len(users):
                        ranks.append("member")
                    ranks[idx] = newrank
                save_ranks(ranks)
                send_room(f"{target} rank set to {newrank}")
            else:
                send_room(f"user {target} not found")

        else:
            send_room("Unknown command or insufficient permissions.")
    except Exception as e:
        send_room(f"Error processing command: {e}")

# helper to notify a specific user (via their socket sessions)
def notify_user(username, payload):
    # payload is arbitrary JSON describing event
    with connected_lock:
        sids = connected.get(username, set()).copy()
    for sid in sids:
        try:
            socketio.emit("user_notify", payload, to=sid)
        except Exception:
            pass

# run
if __name__ == "__main__":
    print("Starting Flask+SocketIO backend on 0.0.0.0:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
