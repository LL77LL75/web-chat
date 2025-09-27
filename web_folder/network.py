# network.py
# Single-file Flask + SocketIO chat with accounts, ranks, persistent rooms, admin commands.
# Run: python network.py
# Requirements: pip install flask flask-socketio eventlet

import os, json, threading, time
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
import random

# -------------------------
# CONFIG / FILE NAMES
# -------------------------
USER_FILE = "usernames.txt"
PWD_FILE = "passwords.txt"
RANK_FILE = "ranks.txt"
ROOMS_FILE = "rooms.json"
SECRET = "E"  # change this for production
PORT = 5000

# -------------------------
# encoding utilities (your code)
# -------------------------
c2n = {**{chr(i+96):i for i in range(1,27)}," ":27,",":28,".":29,"!":30,"/":31}
n2c = {v:k for k,v in c2n.items()}

def enc_py(t):
    # returns nested lists (like your lambda enc)
    result = []
    for ch in t.lower():
        b = bin(c2n[ch])[2:]
        inner = []
        i = 0
        while i < len(b):
            g = random.choice([2, 3])
            segment = b[i:i+g].ljust(g, "0")
            inner.append(int(segment, 2))
            i += g
        result.append(inner)
    return result

def dec_py(d):
    return "".join(n2c[int("".join(bin(g)[2:].zfill(2 if g<4 else 3) for g in grp).lstrip("0") or "0",2)] for grp in d)

# Note: server-side only encoding used for persistence history. Chat messages displayed plain to users.
# If you want end-to-end encryption, we'd need to implement JS side encode/decode too.

# -------------------------
# load/save helpers
# -------------------------
def load_lines(fn):
    if not os.path.exists(fn):
        return []
    with open(fn, "r", encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f.readlines()]

def write_lines(fn, arr):
    with open(fn, "w", encoding="utf-8") as f:
        f.writelines([s+"\n" for s in arr])

def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return {}
    with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rooms(r):
    with open(ROOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2)

# -------------------------
# initial data ensure
# -------------------------
for fname in (USER_FILE, PWD_FILE, RANK_FILE):
    if not os.path.exists(fname):
        open(fname, "a", encoding="utf-8").close()

if not os.path.exists(ROOMS_FILE):
    save_rooms({})

# -------------------------
# Flask app + socketio
# -------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET
socketio = SocketIO(app, cors_allowed_origins="*")

# persistent server-side room state (mirror of rooms.json)
rooms_lock = threading.Lock()
rooms = load_rooms()   # structure: rooms[code] = {"members":[], "hosts":[], "bans":[], "bans_by":[], "mutes":[], "mutes_by":[], "admin_mutes":[], "admin_bans":[], "history":[]}

# ensure fields
def ensure_room(code):
    with rooms_lock:
        if code not in rooms:
            rooms[code] = {"members": [], "hosts": [], "bans": [], "bans_by": [], "mutes": [], "mutes_by": [], "admin_mutes": [], "admin_bans": [], "history": []}
            save_rooms(rooms)

# user helpers
def find_user_index(username):
    users = load_lines(USER_FILE)
    try:
        return users.index(username)
    except ValueError:
        return None

def get_rank(username):
    idx = find_user_index(username)
    if idx is None:
        return None
    ranks = load_lines(RANK_FILE)
    if idx < len(ranks):
        return ranks[idx]
    return "normal"

def set_rank(username, rank):
    users = load_lines(USER_FILE)
    ranks = load_lines(RANK_FILE)
    idx = find_user_index(username)
    if idx is None: return False
    while len(ranks) < len(users):
        ranks.append("normal")
    ranks[idx] = rank
    write_lines(RANK_FILE, ranks)
    return True

def update_credentials(old_username, new_username, new_password):
    users = load_lines(USER_FILE); pwds = load_lines(PWD_FILE); ranks = load_lines(RANK_FILE)
    idx = find_user_index(old_username)
    if idx is None:
        return False
    users[idx] = new_username
    pwds[idx] = new_password
    write_lines(USER_FILE, users); write_lines(PWD_FILE, pwds)
    # ranks line remains aligned
    return True

# -------------------------
# Template strings (simple)
# -------------------------
LOGIN_HTML = """
<!doctype html>
<title>Network Login</title>
<h2>Login</h2>
{% if error %}<p style='color:red'>{{ error }}</p>{% endif %}
<form method="post" action="/">
  <label>Username: <input name="username"></label><br/>
  <label>Password: <input name="password" type="password"></label><br/>
  <button type="submit">Login</button>
</form>
"""

DASH_HTML = """
<!doctype html>
<title>Dashboard</title>
<h2>Welcome, {{ user }} ({{ rank }})</h2>
<div style="display:flex; gap:20px;">
  <div style="flex:1;">
    <h3>Active Rooms</h3>
    <div id="rooms">
      {% for code, info in rooms.items() %}
        <div style="margin:6px;">
          <form method="get" action="/room/{{ code }}" style="display:inline;">
            <button type="submit">{{ code }}</button>
          </form>
        </div>
      {% endfor %}
    </div>
    {% if rank in ['normal','high','core'] %}
    <h4>Create Room</h4>
    <form method="post" action="/create">
      <input name="room" placeholder="room code"/>
      <button>Create</button>
    </form>
    {% endif %}
    <h4>Account</h4>
    <form method="post" action="/changecred">
      <button name="action" value="change">Change username/password</button>
    </form>
    <form method="post" action="/logout"><button>Logout</button></form>
  </div>
  <div style="flex:2;">
    <h3>Selected room</h3>
    <p>Open a room to chat.</p>
    <h3>Admin Tools</h3>
    <div>
      <form method="post" action="/listrooms">
        <button>Refresh Rooms</button>
      </form>
    </div>
  </div>
</div>
"""

ROOM_HTML = """
<!doctype html>
<title>Room {{ room }}</title>
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<h2>Room: {{ room }}</h2>
<p>Logged in as: {{ user }} ({{ rank }})</p>
<div style="display:flex; gap:20px;">
  <div style="width:200px;">
    <h4>Participants</h4>
    <ul id="participants">
      {% for p in participants %}
        <li>{{ p }}</li>
      {% endfor %}
    </ul>
    {% if rank in ['normal','high','core'] %}
      <button onclick="emitCommand('?/showbanned {{ room }}')">Show Banned</button>
      <button onclick="emitCommand('?/showmuted {{ room }}')">Show Muted</button>
    {% endif %}
  </div>
  <div style="flex:1;">
    <div id="messages" style="height:400px; border:1px solid #888; overflow:auto; padding:8px;"></div>
    <div style="margin-top:8px;">
      <input id="msg" style="width:70%"/>
      <button onclick="sendMsg()">Send</button>
    </div>
    <p>Commands: type messages starting with ?/ e.g. ?/mute room alice</p>
  </div>
</div>

<script>
  const socket = io();
  const room = "{{ room }}";
  const user = "{{ user }}";
  socket.on("connect", () => {
    socket.emit("join_room", {"room": room});
  });
  socket.on("chat_message", (m) => {
    const d = document.getElementById("messages");
    d.innerHTML += "<div><strong>"+m.from+"</strong>: "+m.text+"</div>";
    d.scrollTop = d.scrollHeight;
  });
  socket.on("system", (m) => {
    const d = document.getElementById("messages");
    d.innerHTML += "<div style='color:green'><em>"+m+"</em></div>";
    d.scrollTop = d.scrollHeight;
  });
  socket.on("participants", (arr) => {
    const ul = document.getElementById("participants");
    ul.innerHTML = "";
    arr.forEach(p=> ul.innerHTML += "<li>"+p+"</li>");
  });
  function sendMsg(){
    const t = document.getElementById("msg").value;
    if(!t) return;
    socket.emit("send_message", {"room": room, "text": t});
    document.getElementById("msg").value = "";
  }
  function emitCommand(cmd){
    socket.emit("send_message", {"room": room, "text": cmd});
  }
  // handle show lists
  socket.on("banned_list", (data) => {
    alert("Banned in room "+data.room+":\\n" + data.list.join("\\n"));
  });
  socket.on("muted_list", (data) => {
    alert("Muted in room "+data.room+":\\n" + data.list.join("\\n"));
  });
</script>
"""

CHANGE_CRED_HTML = """
<!doctype html>
<title>Change Credentials</title>
<h2>Change username/password</h2>
<form method="post" action="/changecred">
  <label>New username: <input name="newuser" required></label><br/>
  <label>New password: <input name="newpass" required type="password"></label><br/>
  <button type="submit" name="action" value="save">Save</button>
</form>
"""

# -------------------------
# Flask routes
# -------------------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username","").strip()
        pwd = request.form.get("password","").strip()
        users = load_lines(USER_FILE); pwds = load_lines(PWD_FILE)
        if user in users:
            idx = users.index(user)
            if idx < len(pwds) and pwds[idx] == pwd:
                session["user"] = user
                session["rank"] = (load_lines(RANK_FILE)[idx] if idx < len(load_lines(RANK_FILE)) else "normal")
                return redirect(url_for("dashboard"))
        return render_template_string(LOGIN_HTML, error="Invalid credentials")
    return render_template_string(LOGIN_HTML)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    ensure_all_rooms()
    return render_template_string(DASH_HTML, user=session["user"], rank=session["rank"], rooms=rooms)

@app.route("/create", methods=["POST"])
def create_room_route():
    if "user" not in session:
        return redirect(url_for("login"))
    code = request.form.get("room","").strip()
    if code:
        ensure_room(code)
        save_rooms(rooms)
    return redirect(url_for("dashboard"))

@app.route("/room/<room>")
def room_view(room):
    if "user" not in session:
        return redirect(url_for("login"))
    ensure_room(room)
    participants = rooms[room]["members"]
    return render_template_string(ROOM_HTML, room=room, user=session["user"], rank=session["rank"], participants=participants)

@app.route("/changecred", methods=["GET","POST"])
def changecred():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template_string(CHANGE_CRED_HTML)
    # POST - save new credentials
    newu = request.form.get("newuser","").strip()
    newp = request.form.get("newpass","").strip()
    if newu and newp:
        if update_credentials(session["user"], newu, newp):
            session["user"] = newu
            return redirect(url_for("dashboard"))
    return "Failed to update", 400

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------------------------
# socket handlers
# -------------------------
@socketio.on("join_room")
def handle_join(data):
    room = data.get("room")
    user = session.get("user")
    if not user or not room:
        return
    ensure_room(room)
    # enforce bans
    if user in rooms[room]["bans"] or user in rooms[room].get("admin_bans", []):
        emit("system", "You are banned from this room.")
        return
    join_room(room)
    with rooms_lock:
        if user not in rooms[room]["members"]:
            rooms[room]["members"].append(user)
            save_rooms(rooms)
    # notify
    # If admin arrives - special message
    if session.get("rank") in ("core","high","normal") and session.get("rank") is not None:
        if session.get("rank") == "core":
            socketio.emit("system", f"A GOD HAS ARRIVED, {user.upper()}", to=room)
        else:
            socketio.emit("system", f"[{user}] has joined the chat", to=room)
    # broadcast participants
    socketio.emit("participants", rooms[room]["members"], to=room)

@socketio.on("send_message")
def handle_message(data):
    room = data.get("room")
    text = data.get("text","")
    user = session.get("user")
    if not room or not user:
        return
    ensure_room(room)
    # command handling: commands start with "?/"
    if text.startswith("?/"):
        # server-side parse
        parts = text[2:].strip().split()
        if not parts:
            emit("system","Empty command")
            return
        cmd = parts[0].lower()
        args = parts[1:]
        handle_command_server(user, session.get("rank","normal"), room, cmd, args)
        return
    # regular message: enforce mutes/bans
    if user in rooms[room].get("bans",[]) or user in rooms[room].get("admin_bans",[]):
        emit("system","You are banned from this room.")
        return
    if user in rooms[room].get("mutes",[]):
        emit("system","You are muted in this room.")
        return
    if user in rooms[room].get("admin_mutes",[]) and session.get("rank") != "core":
        # admin-muted: only admins (core) see
        emit("system","You are admin-muted.")
        return
    # persist the message encoded (server-side) and broadcast plain text
    encoded = enc_py(text)  # stored for persistence if you want
    with rooms_lock:
        rooms[room]["history"].append({"from": user, "enc": encoded, "ts": time.time()})
        save_rooms(rooms)
    socketio.emit("chat_message", {"from": user, "text": text}, to=room)

# -------------------------
# server-side command parser
# -------------------------
def handle_command_server(issuer, issuer_rank, room, cmd, args):
    """
    Commands syntax (server-side): (no codes required)
      mute [room|admin] [name]
      unmute [room|admin] [name]
      kick [room] [name]
      ban [room|admin] [name]
      unban [room|admin] [name]
      promote [name] [normal|high|core]
      open [room]
      shutdown [room]
      list
      showbanned [room]
      showmuted [room]
    Permissions enforced by issuer_rank: normal/high/core
    """
    cmd = cmd.lower()
    r = room
    # helper functions
    def save_and_notify():
        save_rooms(rooms)
    def is_admin_allowed(level_needed):
        order = {"normal":0,"high":1,"core":2}
        return order.get(issuer_rank,0) >= order.get(level_needed,0)
    # MUTE
    if cmd == "mute" and len(args) >= 2:
        scope = args[0].lower(); target = args[1]
        if scope == "room":
            # host or admin allowed: we'll allow users with any admin rank or if issuer is in hosts
            # for web central model, allow issuer if admin >= normal
            if not is_admin_allowed("normal"):
                socketio.emit("system", "Not allowed", to=room)
                return
            with rooms_lock:
                if target not in rooms[r]["mutes"]:
                    rooms[r]["mutes"].append(target); rooms[r]["mutes_by"].append(issuer)
                    save_and_notify()
            socketio.emit("system", f"{target} muted in {r} by {issuer}", to=r)
            return
        elif scope == "admin":
            # admin/global mute - only high+ or core?
            if not is_admin_allowed("high"):
                socketio.emit("system", "Admin-scope mute requires high/core admin", to=r)
                return
            with rooms_lock:
                if target not in rooms[r].get("admin_mutes",[]):
                    rooms[r].setdefault("admin_mutes",[]).append(target)
                    save_and_notify()
            socketio.emit("system", f"{target} admin-muted by {issuer}", to=r)
            return
    # UNMUTE
    if cmd == "unmute" and len(args) >= 2:
        scope = args[0].lower(); target = args[1]
        if scope == "room":
            if not is_admin_allowed("normal"):
                socketio.emit("system","Not allowed",to=r); return
            with rooms_lock:
                if target in rooms[r]["mutes"]:
                    idx = rooms[r]["mutes"].index(target)
                    rooms[r]["mutes"].pop(idx); rooms[r]["mutes_by"].pop(idx)
                    save_and_notify()
            socketio.emit("system", f"{target} unmuted in {r} by {issuer}", to=r)
            return
        elif scope == "admin":
            if not is_admin_allowed("core"):
                socketio.emit("system","Only core admin can admin-unmute",to=r); return
            with rooms_lock:
                if target in rooms[r].get("admin_mutes",[]): rooms[r]["admin_mutes"].remove(target); save_and_notify()
            socketio.emit("system", f"{target} admin-unmuted by {issuer}", to=r)
            return
    # KICK
    if cmd == "kick" and len(args) >= 2:
        scope = args[0].lower(); target = args[1]
        if scope == r:
            with rooms_lock:
                if target in rooms[r]["members"]:
                    rooms[r]["members"].remove(target)
                    save_and_notify()
            socketio.emit("system", f"{target} was kicked from {r} by {issuer}", to=r)
            return
    # BAN
    if cmd == "ban" and len(args) >= 2:
        scope = args[0].lower(); target = args[1]
        if scope == r:
            if not is_admin_allowed("normal"):
                socketio.emit("system","Not allowed",to=r); return
            with rooms_lock:
                if target not in rooms[r]["bans"]:
                    rooms[r]["bans"].append(target); rooms[r]["bans_by"].append(issuer); save_and_notify()
            socketio.emit("system", f"{target} banned from {r} by {issuer}", to=r)
            return
        elif scope == "admin":
            if not is_admin_allowed("core"):
                socketio.emit("system","Only core admin can ban globally",to=r); return
            with rooms_lock:
                # add to admin_bans across all rooms
                for rc in rooms:
                    if target not in rooms[rc].get("admin_bans",[]): rooms[rc].setdefault("admin_bans",[]).append(target)
                save_and_notify()
            socketio.emit("system", f"{target} globally banned by {issuer}", broadcast=True)
            return
    # UNBAN
    if cmd == "unban" and len(args) >= 2:
        scope = args[0].lower(); target = args[1]
        if scope == r:
            if not is_admin_allowed("normal"):
                socketio.emit("system","Not allowed",to=r); return
            with rooms_lock:
                if target in rooms[r]["bans"]:
                    idx = rooms[r]["bans"].index(target); rooms[r]["bans"].pop(idx); rooms[r]["bans_by"].pop(idx); save_and_notify()
            socketio.emit("system", f"{target} unbanned in {r} by {issuer}", to=r)
            return
        elif scope == "admin":
            if not is_admin_allowed("core"):
                socketio.emit("system","Only core admin can unban globally",to=r); return
            with rooms_lock:
                for rc in rooms:
                    if target in rooms[rc].get("admin_bans",[]): rooms[rc]["admin_bans"].remove(target)
                save_and_notify()
            socketio.emit("system", f"{target} globally unbanned by {issuer}", broadcast=True)
            return
    # PROMOTE
    if cmd == "promote" and len(args) >= 2:
        if not is_admin_allowed("core"):
            socketio.emit("system","Only core admins can promote",to=r); return
        target = args[0]; newrank = args[1]
        if newrank not in ("normal","high","core"):
            socketio.emit("system","Invalid rank",to=r); return
        if set_rank(target, newrank):
            socketio.emit("system", f"{target} promoted to {newrank} by {issuer}", to=r)
        else:
            socketio.emit("system","User not found",to=r)
        return
    # OPEN
    if cmd == "open" and len(args) >= 1:
        if not is_admin_allowed("normal"):
            socketio.emit("system","Only admins can open rooms",to=r); return
        newr = args[0]
        ensure_room(newr)
        save_rooms(rooms)
        socketio.emit("system", f"Room {newr} opened by {issuer}", to=r)
        return
    # SHUTDOWN
    if cmd == "shutdown" and len(args) >= 1:
        if not is_admin_allowed("normal"):
            socketio.emit("system","Only admins can shutdown rooms",to=r); return
        tgt = args[0]
        with rooms_lock:
            if tgt in rooms:
                del rooms[tgt]; save_and_notify()
        socketio.emit("system", f"Room {tgt} shutdown by {issuer}", broadcast=True)
        return
    # LIST
    if cmd == "list":
        socketio.emit("system", "Active rooms: " + ", ".join(list(rooms.keys())), to=r)
        return
    # showbanned/showmuted
    if cmd == "showbanned" and len(args)>=1:
        tgt = args[0]
        if tgt in rooms:
            socketio.emit("banned_list", {"room":tgt, "list": rooms[tgt].get("bans",[])}, to=request.sid)
        else:
            socketio.emit("system", "Room not found", to=request.sid)
        return
    if cmd == "showmuted" and len(args)>=1:
        tgt = args[0]
        if tgt in rooms:
            socketio.emit("muted_list", {"room":tgt, "list": rooms[tgt].get("mutes",[])}, to=request.sid)
        else:
            socketio.emit("system", "Room not found", to=request.sid)
        return
    socketio.emit("system", "Unknown command or bad args", to=r)

# -------------------------
# housekeeping helpers
# -------------------------
def ensure_all_rooms():
    # ensure each room has required keys
    with rooms_lock:
        for code in list(rooms.keys()):
            ensure_room(code)

# -------------------------
# run
# -------------------------
if __name__ == "__main__":
    print("Starting network.py web chat (Flask + SocketIO).")
    print("Make sure usernames.txt, passwords.txt, ranks.txt exist in this folder (linewise entries).")
    socketio.run(app, host="0.0.0.0", port=PORT)
