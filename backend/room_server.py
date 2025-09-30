from flask import Flask, request
from flask_socketio import SocketIO, emit
import sys, time, json, os, random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

USERS = []          # connected usernames
BANS = {}           # username -> ban_level
MUTES = {}          # username -> mute_level
USER_RANKS = {}     # username -> rank

ROOM_CODE = None
MESSAGES_FILE = None
MESSAGES = []       # stored messages


# -------- Helpers --------
def now_ts():
    return time.strftime("%I:%M %p")

def make_id():
    return f"{time.time():.6f}-{random.randint(1000,9999)}"

def load_messages():
    global MESSAGES
    if MESSAGES_FILE and os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
                MESSAGES = json.load(f)
        except Exception:
            MESSAGES = []
    else:
        MESSAGES = []

def save_messages():
    if not MESSAGES_FILE:
        return
    try:
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(MESSAGES, f, indent=2)
    except Exception as e:
        print("Error saving messages:", e)

def load_users():
    path = os.path.join(os.path.dirname(__file__), "usernames.txt")
    return [l.strip() for l in open(path)] if os.path.exists(path) else []

def load_passwords():
    path = os.path.join(os.path.dirname(__file__), "passwords.txt")
    return [l.strip() for l in open(path)] if os.path.exists(path) else []

def load_ranks():
    path = os.path.join(os.path.dirname(__file__), "ranks.txt")
    return [l.strip() for l in open(path)] if os.path.exists(path) else []

def verify_credentials(username, password):
    users = load_users()
    pwds = load_passwords()
    ranks = load_ranks()
    if username in users:
        idx = users.index(username)
        if idx < len(pwds) and pwds[idx] == password:
            rank = ranks[idx] if idx < len(ranks) else "newbie"
            USER_RANKS[username] = rank
            return True
    return False


# -------- Socket Handlers --------
@socketio.on("connect")
def _on_connect():
    emit("sys", {"msg": f"connected to room server {ROOM_CODE}"})


@socketio.on("join")
def handle_join(data):
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        emit("sys", {"msg": "missing username or password"})
        return

    if not verify_credentials(username, password):
        emit("sys", {"msg": "invalid credentials"})
        return

    if username in BANS:
        emit("sys", {"msg": f"You are banned (level {BANS[username]})"})
        return

    if username not in USERS:
        USERS.append(username)

    emit("history", MESSAGES)

    emit("message", {
        "id": make_id(),
        "user": "Server",
        "msg": f"{username} ({USER_RANKS[username]}) joined the room.",
        "time": now_ts(),
        "edited": False,
        "edited_time": None
    }, broadcast=True)


@socketio.on("leave")
def handle_leave(data):
    username = (data.get("username") or "").strip()
    try:
        if username in USERS:
            USERS.remove(username)
    except ValueError:
        pass
    emit("message", {
        "id": make_id(),
        "user": "Server",
        "msg": f"{username} left the room.",
        "time": now_ts(),
        "edited": False,
        "edited_time": None
    }, broadcast=True)


@socketio.on("chat")
def handle_chat(data):
    username = (data.get("username") or "").strip()
    text = data.get("msg") or ""

    if not username or text is None:
        return

    # commands
    if text.startswith("?/"):
        handle_command(username, text)
        return

    if username in MUTES:
        emit("sys", {"msg": f"You are muted (level {MUTES[username]})."})
        return

    msg = {
        "id": make_id(),
        "user": username,
        "msg": text,
        "time": now_ts(),
        "edited": False,
        "edited_time": None
    }
    MESSAGES.append(msg)
    save_messages()
    emit("message", msg, broadcast=True)


@socketio.on("delete_message")
def handle_delete(data):
    username = (data.get("username") or "").strip()
    msg_id = data.get("id")
    if not username or not msg_id:
        return
    for m in list(MESSAGES):
        if m.get("id") == msg_id:
            if m.get("user") == username:
                MESSAGES.remove(m)
                save_messages()
                emit("delete", {"id": msg_id}, broadcast=True)
            else:
                emit("sys", {"msg": "You can only delete your own messages."})
            return


@socketio.on("edit_message")
def handle_edit(data):
    username = (data.get("username") or "").strip()
    msg_id = data.get("id")
    new_text = data.get("new")
    if not username or not msg_id or new_text is None:
        return
    for m in MESSAGES:
        if m.get("id") == msg_id:
            if m.get("user") == username:
                m["msg"] = new_text
                m["edited"] = True
                m["edited_time"] = now_ts()
                save_messages()
                emit("edit", m, broadcast=True)
            else:
                emit("sys", {"msg": "You can only edit your own messages."})
            return


# -------- Commands --------
def handle_command(actor, text):
    rank = USER_RANKS.get(actor, "newbie")
    parts = text[2:].strip().split()
    if not parts:
        return
    cmd = parts[0].lower()
    args = parts[1:]

    # newbie restriction
    if rank == "newbie":
        emit("sys", {"msg": "You are a newbie and cannot use commands."})
        return

    # member can only use ?/msg
    if rank == "member" and cmd != "msg":
        emit("sys", {"msg": "You are a member and cannot use that command."})
        return

    if cmd == "msg" and len(args) >= 2:
        target = args[0]
        message_text = " ".join(args[1:])
        emit("sys", {"msg": f"[PM from {actor}]: {message_text}"}, to=request.sid)
        # for simplicity we broadcast PM visibly to target
        emit("sys", {"msg": f"[PM to {target}]: {message_text}"}, broadcast=True)
        return

    # admin-only commands
    if cmd == "ban" and len(args) >= 2:
        target, level = args[0], args[1]
        BANS[target] = level
        broadcast_sys(f"{target} banned (level {level})")

    elif cmd == "unban" and len(args) >= 1:
        target = args[0]
        BANS.pop(target, None)
        broadcast_sys(f"{target} unbanned")

    elif cmd == "mute" and len(args) >= 2:
        target, level = args[0], args[1]
        MUTES[target] = level
        broadcast_sys(f"{target} muted (level {level})")

    elif cmd == "unmute" and len(args) >= 1:
        target = args[0]
        MUTES.pop(target, None)
        broadcast_sys(f"{target} unmuted")

    elif cmd == "kick" and len(args) >= 1:
        target = args[0]
        if target in USERS:
            try:
                USERS.remove(target)
            except ValueError:
                pass
        broadcast_sys(f"{target} kicked")

    else:
        emit("sys", {"msg": "Unknown command or not allowed."})


def broadcast_sys(message):
    emit("message", {
        "id": make_id(),
        "user": "Server",
        "msg": message,
        "time": now_ts(),
        "edited": False,
        "edited_time": None
    }, broadcast=True)


# -------- Startup --------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python room_server.py <port> <room_code>")
        sys.exit(1)

    port = int(sys.argv[1])
    ROOM_CODE = sys.argv[2]
    MESSAGES_FILE = os.path.join(os.path.dirname(__file__), f"room_{ROOM_CODE}_messages.json")
    load_messages()
    print(f"Room '{ROOM_CODE}' running on port {port}")
    socketio.run(app, host="0.0.0.0", port=port)
