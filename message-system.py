# #!/usr/bin/env python3
# """
# mesh_chat_persist.py

# Single-file rendezvous + mesh chat with:
# - multi-host mesh
# - admins (password protected)
# - join notifications (including "A GOD HAS ARRIVED, NAME" for admins)
# - commands: ?/mute ?/unmute ?/kick ?/ban ?/unban with room/admin scopes
# - persistence of rendezvous state (rooms, bans, mutes, admin_pass) to rendezvous_state.json
# - run as "rendezvous" on a public server; run as "chat" for peers

# Save and run:
#   python mesh_chat_persist.py
# """

import socket, threading, json, time, sys, os
list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ',',','.']
def binary(num):
    return bin(num)[2:]
    binary_string = binary(num)
def num(binary_item):
    binary_str = str(binary_item)
    return int(binary_item, 2)

message = input("Enter a message: ")
import random
def heck(num):
    binary_str = bin(num)[2:] 
    numbers = []
    i = 0
    while i < len(binary_str):
        group_size = random.choice([2, 3])
        group = binary_str[i:i+group_size]
        if len(group) < group_size:
            group += "0" * (group_size - len(group))
        numbers.append(int(group, 2))
        i += group_size
    return numbers
def unheck(num):
    binary_str = ""
    for number in num:
        binary_str += bin(number)[2:]
    return int(binary_str, 2)    

CHAT_PORT = 5050
RENDEZVOUS_PORT = 6000
STATE_FILE = "rendezvous_state.json"
LOCK = threading.Lock()

# Rendezvous persistent state (loaded/saved by rendezvous mode)
pstate = {
    "rooms": {},       # room_code -> {"hosts": [[ip,port,name],...], "mutes": [], "admin_mutes": [], "bans": []}
    "global_bans": [], # names
    "global_mutes": [],# names muted globally by admin
    "admin_pass": None
}

# ---------- util JSON send/recv ----------
def send_json(sock, obj):
    try:
        sock.sendall((json.dumps(obj) + "\n").encode())
    except:
        pass

def recv_json(sock, timeout=None):
    # read until newline or return None
    try:
        sock.settimeout(timeout)
        data = b""
        while True:
            part = sock.recv(4096)
            if not part:
                break
            data += part
            if b"\n" in part:
                break
        sock.settimeout(None)
        if not data:
            return None
        line = data.split(b"\n",1)[0]
        return json.loads(line.decode(errors="ignore"))
    except:
        return None

# ---------- persistence helpers ----------
def load_state():
    global pstate
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                pstate = json.load(f)
            # ensure types
            if "rooms" not in pstate: pstate["rooms"] = {}
            if "global_bans" not in pstate: pstate["global_bans"] = []
            if "global_mutes" not in pstate: pstate["global_mutes"] = []
            if "admin_pass" not in pstate: pstate["admin_pass"] = None
        except Exception as e:
            print("[Rendezvous] Failed to load state:", e)
            pstate = {"rooms": {}, "global_bans": [], "global_mutes": [], "admin_pass": None}
    else:
        save_state()

def save_state():
    try:
        with LOCK:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(pstate, f, indent=2)
    except Exception as e:
        print("[Rendezvous] Failed to save state:", e)

# ---------- Rendezvous server handlers ----------
def rendezvous_handle(csock, addr):
    global pstate
    try:
        req = recv_json(csock)
        if not req:
            return
        typ = req.get("type")
        if typ == "JOIN":
            code = req.get("code")
            name = req.get("name")
            is_admin_attempt = req.get("is_admin", False)
            passwd = req.get("admin_pass", "")
            # check global ban
            with LOCK:
                if name in pstate.get("global_bans", []):
                    send_json(csock, {"type":"DENIED","reason":"GLOBAL_BANNED"})
                    return
                # ensure room exists
                if code not in pstate["rooms"]:
                    pstate["rooms"][code] = {"hosts": [], "mutes": [], "admin_mutes": [], "bans": []}
                    save_state()
                # room ban check
                if name in pstate["rooms"][code].get("bans", []):
                    send_json(csock, {"type":"DENIED","reason":"ROOM_BANNED"})
                    return
                # admin auth check
                auth_ok = False
                if is_admin_attempt and pstate.get("admin_pass") and passwd == pstate["admin_pass"]:
                    auth_ok = True
                # build host list
                hosts = [{"ip":h[0], "port":h[1], "name":h[2]} for h in pstate["rooms"][code]["hosts"]]
                send_json(csock, {
                    "type":"JOINED",
                    "hosts": hosts,
                    "mutes": pstate["rooms"][code]["mutes"],
                    "admin_mutes": pstate["rooms"][code]["admin_mutes"],
                    "bans": pstate["rooms"][code]["bans"],
                    "global_bans": pstate["global_bans"],
                    "global_mutes": pstate["global_mutes"],
                    "admin_ok": auth_ok
                })
                return

        elif typ == "ANNOUNCE":
            code = req.get("code"); port = req.get("port", CHAT_PORT); name = req.get("name","")
            with LOCK:
                if code not in pstate["rooms"]:
                    pstate["rooms"][code] = {"hosts": [], "mutes": [], "admin_mutes": [], "bans": []}
                tup = (addr[0], port, name)
                # add if not present
                if [addr[0], port, name] not in pstate["rooms"][code]["hosts"]:
                    pstate["rooms"][code]["hosts"].append([addr[0], port, name])
                    save_state()
            send_json(csock, {"type":"ANNOUNCED","ok":True})
            return

        elif typ == "REMOVE_HOST":
            code = req.get("code"); port = req.get("port", CHAT_PORT); name = req.get("name","")
            with LOCK:
                r = pstate["rooms"].get(code)
                if r:
                    r["hosts"] = [h for h in r["hosts"] if not (h[0]==addr[0] and h[1]==port and h[2]==name)]
                    save_state()
            send_json(csock, {"type":"REMOVED"})
            return

        elif typ == "SET_PASS":
            passwd = req.get("password")
            with LOCK:
                pstate["admin_pass"] = passwd
                save_state()
            send_json(csock, {"type":"PASS_SET","ok":True})
            return

        elif typ == "VERIFY_ADMIN":
            passwd = req.get("password","")
            ok = (pstate.get("admin_pass") is not None and passwd == pstate["admin_pass"])
            send_json(csock, {"type":"VERIFIED","ok": ok})
            return

        elif typ == "QUERY_HOSTS":
            code = req.get("code")
            with LOCK:
                r = pstate["rooms"].get(code, {"hosts":[]})
                hosts = [{"ip":h[0], "port":h[1], "name":h[2]} for h in r["hosts"]]
            send_json(csock, {"type":"HOSTS","hosts":hosts})
            return

        else:
            send_json(csock, {"type":"UNKNOWN"})
            return
    except Exception:
        pass
    finally:
        try: csock.close()
        except: pass

def rendezvous_server():
    load_state()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", RENDEZVOUS_PORT))
    s.listen()
    print(f"[Rendezvous] Listening on port {RENDEZVOUS_PORT}")
    print("Commands: setpass <password> | showrooms | quit")
    def accept_loop():
        while True:
            try:
                c,a = s.accept()
                threading.Thread(target=rendezvous_handle, args=(c,a), daemon=True).start()
            except:
                break
    threading.Thread(target=accept_loop, daemon=True).start()

    while True:
        try:
            cmdline = input("> ").strip()
        except EOFError:
            break
        if not cmdline:
            continue
        parts = cmdline.split()
        cmd = parts[0].lower()
        if cmd == "setpass" and len(parts) >= 2:
            passwd = " ".join(parts[1:])
            with LOCK:
                pstate["admin_pass"] = passwd
                save_state()
            print("[Rendezvous] Admin password set.")
        elif cmd == "showrooms":
            with LOCK:
                print(json.dumps(pstate, indent=2))
        elif cmd == "quit":
            print("[Rendezvous] shutting down.")
            try:
                s.close()
            except:
                pass
            break
        else:
            print("Unknown. Commands: setpass <password> | showrooms | quit")

# ---------- Peer / Chat mesh logic ----------
# Message types:
# CHAT: {"type":"CHAT","room":code,"from":name,"text":text}
# JOIN_NOTIFY: {"type":"JOIN_NOTIFY","room":code,"name":name,"is_admin":bool}
# CMD: {"type":"CMD","room":code,"from":name,"cmd":"mute","args":[...],"auth":{"is_admin":bool}}
# STATE: {"type":"STATE","room":code,"mutes":[], "admin_mutes":[], "bans":[], "global_mutes": [], "global_bans": []}
# KICK: {"type":"KICK","room":code,"target":name}
# META HELLO: {"type":"META","sub":"HELLO","name":name}

class Peer:
    def __init__(self, rendezvous_ip, name, is_admin=False, admin_pass_try=""):
        self.rendezvous_ip = rendezvous_ip
        self.name = name
        self.is_admin = is_admin
        self.admin_authed = False
        self.admin_pass_try = admin_pass_try
        self.room = None
        self.listen_sock = None
        self.peers_lock = threading.Lock()
        self.host_conns = {}    # (ip,port) -> socket (outgoing)
        self.local_conns = []   # sockets accepted (incoming)
        # room state mirrored from rendezvous or propagated by peers
        self.room_state = {"mutes": set(), "admin_mutes": set(), "bans": set(), "global_bans": set(), "global_mutes": set() }
        self.running = True

    # Rendezvous interactions
    def rendezvous_join(self, code):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.rendezvous_ip, RENDEZVOUS_PORT))
            send_json(s, {"type":"JOIN","code":code,"name":self.name,"is_admin": self.is_admin, "admin_pass": self.admin_pass_try})
            resp = recv_json(s, timeout=5)
            s.close()
            return resp
        except Exception as e:
            print("[Error] rendezvous unreachable:", e)
            return None

    def rendezvous_announce(self, code):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.rendezvous_ip, RENDEZVOUS_PORT))
            send_json(s, {"type":"ANNOUNCE","code":code,"port":CHAT_PORT,"name": self.name})
            recv_json(s, timeout=3)
            s.close()
        except Exception:
            pass

    def rendezvous_remove(self, code):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.rendezvous_ip, RENDEZVOUS_PORT))
            send_json(s, {"type":"REMOVE_HOST","code":code,"port":CHAT_PORT,"name": self.name})
            recv_json(s, timeout=2)
            s.close()
        except:
            pass

    def attempt_admin_verify(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.rendezvous_ip, RENDEZVOUS_PORT))
            send_json(s, {"type":"VERIFY_ADMIN","password": self.admin_pass_try})
            r = recv_json(s, timeout=3)
            s.close()
            if r and r.get("type") == "VERIFIED" and r.get("ok"):
                self.admin_authed = True
                return True
        except:
            pass
        return False

    # Listening for incoming peer connections
    def start_listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", CHAT_PORT))
        s.listen()
        self.listen_sock = s
        def accept_loop():
            while self.running:
                try:
                    c,a = s.accept()
                    with self.peers_lock:
                        self.local_conns.append(c)
                    threading.Thread(target=self.handle_incoming, args=(c,a), daemon=True).start()
                except:
                    break
        threading.Thread(target=accept_loop, daemon=True).start()

    def handle_incoming(self, sock, addr):
        # we expect JSON lines
        while self.running:
            m = recv_json(sock)
            if not m:
                break
            self.process_message(m, sock, addr)
        try: sock.close()
        except: pass
        with self.peers_lock:
            if sock in self.local_conns:
                self.local_conns.remove(sock)

    def connect_to_host(self, ip, port):
        # attempt outgoing connection if not already connected
        try:
            key = (ip, port)
            with self.peers_lock:
                if key in self.host_conns:
                    return
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip, port))
            s.settimeout(None)
            with self.peers_lock:
                self.host_conns[key] = s
            # start recv loop
            threading.Thread(target=self.peer_recv_loop, args=(s,key), daemon=True).start()
            send_json(s, {"type":"META","sub":"HELLO","name":self.name})
        except Exception:
            pass

    def peer_recv_loop(self, sock, key):
        while self.running:
            m = recv_json(sock)
            if not m:
                break
            self.process_message(m, sock, key)
        # cleanup
        with self.peers_lock:
            if key in self.host_conns and self.host_conns[key] == sock:
                del self.host_conns[key]
        try: sock.close()
        except: pass

    def broadcast(self, obj):
        raw = (json.dumps(obj) + "\n").encode()
        with self.peers_lock:
            conns = list(self.host_conns.values()) + list(self.local_conns)
        for c in conns:
            try:
                c.sendall(raw)
            except:
                pass

    # handle incoming protocol messages
    def process_message(self, m, sock, addr):
        typ = m.get("type")
        if typ == "CHAT":
            room = m.get("room")
            sender = m.get("from")
            text = m.get("text")
            # enforce global and room bans/mutes
            if sender in self.room_state["global_bans"] or sender in self.room_state["bans"]:
                return
            if sender in self.room_state["global_mutes"]:
                # only admins see admin-muted users' messages; non-admins should not see them
                # since this is a peer, simply drop if viewer is not admin
                # but we print to local console only if this peer is admin
                if not (self.is_admin and self.admin_authed):
                    return
            if sender in self.room_state["admin_mutes"]:
                # admin mute acts like global_mute but stored per room
                if not (self.is_admin and self.admin_authed):
                    return
            if sender in self.room_state["mutes"]:
                return
            # regular print
            print(f"\n[{sender}]: {text}")
        elif typ == "JOIN_NOTIFY":
            room = m.get("room"); who = m.get("name"); isadm = m.get("is_admin", False)
            if room == self.room:
                if isadm:
                    god = f"A GOD HAS ARRIVED, {who.upper()}"
                    print("\n" + god)
                else:
                    print(f"\n[{who}] has joined the chat")
        elif typ == "CMD":
            # a command propagated by a host/admin
            cmd = m.get("cmd"); args = m.get("args", []); issuer = m.get("from"); auth = m.get("auth", {})
            # we trust hosts/admins but enforce admin-only constraints
            self.apply_command_local(issuer, cmd, args, auth, propagate=False)
        elif typ == "STATE":
            # synchronize state
            room = m.get("room")
            if room != self.room:
                return
            self.room_state["mutes"] = set(m.get("mutes", []))
            self.room_state["admin_mutes"] = set(m.get("admin_mutes", []))
            self.room_state["bans"] = set(m.get("bans", []))
            self.room_state["global_bans"] = set(m.get("global_bans", []))
            self.room_state["global_mutes"] = set(m.get("global_mutes", []))
            # no printed message needed
        elif typ == "KICK":
            target = m.get("target"); room = m.get("room")
            if target == self.name and room == self.room:
                print("\n[System] You have been kicked from this room.")
                self.leave_room()
        elif typ == "META":
            # ignore or handle HELLO
            pass

    # apply a command locally (and optionally propagate)
    def apply_command_local(self, issuer, cmd, args, auth, propagate=True):
        # Determine permission:
        # - admin-scoped actions require auth['is_admin'] True
        # - room-scoped actions allowed by hosts (we accept commands from hosts since mesh hosts are trustees)
        is_admin_action = False
        cmd_l = cmd.lower()
        if cmd_l in ("ban","unban","mute","unmute") and len(args) >= 2:
            scope = args[1].lower()
            if scope == "admin":
                is_admin_action = True
        # check auth
        if is_admin_action and not auth.get("is_admin", False):
            print("[System] Admin-scope command rejected: admin privileges required.")
            return

        # perform actions
        if cmd_l == "mute" and len(args) >= 2:
            target = args[0]; scope = args[1].lower()
            if scope == "admin":
                # admin/global mute (affects all rooms). Only admins allowed (already checked)
                self.room_state["global_mutes"].add(target)
                if propagate:
                    self.broadcast({"type":"CMD","from":issuer,"cmd":"mute","args":[target,"admin"],"auth":auth})
                    self.broadcast_state()
                print(f"[System] {target} globally admin-muted.")
            else:
                # room mute
                if scope == self.room:
                    self.room_state["mutes"].add(target)
                    if propagate:
                        self.broadcast({"type":"CMD","from":issuer,"cmd":"mute","args":[target,scope],"auth":auth})
                        self.broadcast_state()
                    print(f"[System] {target} muted in room {scope}")
        elif cmd_l == "unmute" and len(args) >= 2:
            target = args[0]; scope = args[1].lower()
            if scope == "admin":
                # only admin can unmute admin-muted users
                if target in self.room_state["global_mutes"]:
                    self.room_state["global_mutes"].remove(target)
                    if propagate:
                        self.broadcast({"type":"CMD","from":issuer,"cmd":"unmute","args":[target,"admin"],"auth":auth})
                        self.broadcast_state()
                    print(f"[System] {target} globally unmuted (admin).")
                if target in self.room_state["admin_mutes"]:
                    self.room_state["admin_mutes"].remove(target)
                    if propagate:
                        self.broadcast({"type":"CMD","from":issuer,"cmd":"unmute","args":[target,"admin"],"auth":auth})
                        self.broadcast_state()
                    print(f"[System] {target} admin-unmuted in room.")
            else:
                if scope == self.room and target in self.room_state["mutes"]:
                    self.room_state["mutes"].remove(target)
                    if propagate:
                        self.broadcast({"type":"CMD","from":issuer,"cmd":"unmute","args":[target,scope],"auth":auth})
                        self.broadcast_state()
                    print(f"[System] {target} unmuted in room {scope}")
        elif cmd_l == "kick" and len(args) >= 2:
            target = args[0]; scope = args[1].lower()
            if scope == self.room:
                self.broadcast({"type":"KICK","room":scope,"target":target})
                print(f"[System] {target} kicked from {scope}")
        elif cmd_l == "ban" and len(args) >= 2:
            target = args[0]; scope = args[1].lower()
            if scope == "admin":
                # admin global ban (admin-only)
                self.room_state["global_bans"].add(target)
                if propagate:
                    self.broadcast({"type":"CMD","from":issuer,"cmd":"ban","args":[target,"admin"],"auth":auth})
                    self.broadcast_state()
                print(f"[System] {target} globally banned (admin).")
            else:
                if scope == self.room:
                    self.room_state["bans"].add(target)
                    if propagate:
                        self.broadcast({"type":"CMD","from":issuer,"cmd":"ban","args":[target,scope],"auth":auth})
                        self.broadcast_state()
                    print(f"[System] {target} banned from room {scope}")
        elif cmd_l == "unban" and len(args) >= 2:
            target = args[0]; scope = args[1].lower()
            if scope == "admin":
                if target in self.room_state["global_bans"]:
                    self.room_state["global_bans"].remove(target)
                    if propagate:
                        self.broadcast({"type":"CMD","from":issuer,"cmd":"unban","args":[target,"admin"],"auth":auth})
                        self.broadcast_state()
                    print(f"[System] {target} unbanned globally (admin).")
            else:
                if scope == self.room and target in self.room_state["bans"]:
                    self.room_state["bans"].remove(target)
                    if propagate:
                        self.broadcast({"type":"CMD","from":issuer,"cmd":"unban","args":[target,scope],"auth":auth})
                        self.broadcast_state()
                    print(f"[System] {target} unbanned from room {scope}")
        else:
            print("[System] Unknown command or bad args.")

    def broadcast_state(self):
        obj = {"type":"STATE","room":self.room,
               "mutes": list(self.room_state["mutes"]),
               "admin_mutes": list(self.room_state["admin_mutes"]),
               "bans": list(self.room_state["bans"]),
               "global_bans": list(self.room_state["global_bans"]),
               "global_mutes": list(self.room_state["global_mutes"])}
        self.broadcast(obj)

    def get_public_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def leave_room(self):
        self.running = False
        try:
            if self.listen_sock:
                self.listen_sock.close()
        except:
            pass
        with self.peers_lock:
            for s in list(self.host_conns.values()) + list(self.local_conns):
                try: s.close()
                except: pass
            self.host_conns.clear()
            self.local_conns.clear()
        try:
            self.rendezvous_remove(self.room)
        except:
            pass
        print("[System] Left room. Exiting.")
        sys.exit(0)

    # main run: join rendezvous, announce, connect to hosts, start CLI
    def run(self, code):
        self.room = code
        resp = self.rendezvous_join(code)
        if not resp:
            print("[Error] No rendezvous response. Abort.")
            return
        if resp.get("type") == "DENIED":
            print("[System] You are banned:", resp.get("reason"))
            return
        # apply initial state
        self.room_state["mutes"] = set(resp.get("mutes", []))
        self.room_state["admin_mutes"] = set(resp.get("admin_mutes", []))
        self.room_state["bans"] = set(resp.get("bans", []))
        self.room_state["global_bans"] = set(resp.get("global_bans", []))
        self.room_state["global_mutes"] = set(resp.get("global_mutes", []))
        if resp.get("admin_ok"):
            self.admin_authed = True

        # announce to rendezvous so future joiners know hosts
        self.rendezvous_announce(code)

        # start listening for incoming peer connections
        self.start_listen()
        time.sleep(0.2)

        # connect to each returned host
        hosts = resp.get("hosts", [])
        for h in hosts:
            hip = h.get("ip"); hport = h.get("port", CHAT_PORT)
            if hip == self.get_public_ip() and h.get("name") == self.name:
                continue
            threading.Thread(target=self.connect_to_host, args=(hip, hport), daemon=True).start()
        time.sleep(0.5)

        # announce join to mesh
        # notify all peers of join
        join_msg = {"type":"JOIN_NOTIFY","room":self.room,"name":self.name,"is_admin": (self.is_admin and (self.admin_authed or self.attempt_admin_verify()))}
        self.broadcast(join_msg)
        # local print of join
        if join_msg["is_admin"]:
            print("A GOD HAS ARRIVED, " + self.name.upper())
        else:
            print(f"[{self.name}] has joined the chat (you)")

        # CLI loop
        print("[System] Joined room:", self.room)
        print("[System] Type messages. Commands start with '?/'")
        while True:
            try:
                line = input()
            except EOFError:
                line = "/quit"
            if not line:
                continue
            if line.strip() == "/quit":
                self.leave_room()
            if line.startswith("?/"):
                parts = line[2:].strip().split()
                if not parts:
                    print("[System] Empty command")
                    continue
                cmd = parts[0].lower(); args = parts[1:]
                auth = {"is_admin": self.is_admin and self.admin_authed}
                # apply locally and propagate
                self.apply_command_local(self.name, cmd, args, auth, propagate=True)
            else:
                # send chat object to all hosts (mesh). hosts will forward appropriately.
                # local enforcement: if you are banned, don't send; if muted, you can send but others will not see
                if self.name in self.room_state["global_bans"] or self.name in self.room_state["bans"]:
                    print("[System] You are banned and cannot send.")
                    continue
                obj = {"type":"CHAT","room":self.room,"from":self.name,"text":line}
                # print local echo unless you're muted from view (admins may still see)
                print(f"[{self.name}]: {line}")
                self.broadcast(obj)

# ---------- Mode runners ----------
def run_rendezvous_mode():
    print("Starting rendezvous server (with persistence).")
    rendezvous_server()

def run_chat_mode():
    print("Chat client mode.")
    rendezvous_ip = input("Rendezvous server IP (public server; use 127.0.0.1 for local): ").strip()
    if not rendezvous_ip:
        rendezvous_ip = "127.0.0.1"
    name = input("Enter your name: ").strip()
    is_admin = input("Are you an admin? (y/n): ").strip().lower().startswith("y")
    admin_pass_try = ""
    if is_admin:
        admin_pass_try = input("Enter admin password: ").strip()
    p = Peer(rendezvous_ip, name, is_admin=is_admin, admin_pass_try=admin_pass_try)
    code = input("Enter chat code (room): ").strip()
    p.run(code)

if __name__ == "__main__":
    print("mesh_chat_persist.py — single-file rendezvous + mesh chat with persistence")
    print("Modes: 'rendezvous' to run discovery/persistence; 'chat' to join a room (peers)")
    mode = input("Run as (rendezvous/chat): ").strip().lower()
    if mode == "rendezvous":
        run_rendezvous_mode()
    else:
        run_chat_mode()
# ---------- End of file ----------