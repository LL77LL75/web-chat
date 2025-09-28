// Small, complete frontend to talk to our Flask+SocketIO backend
const socket = io();

let TOKEN = null;
let CURRENT_ROOM = null;
let USERNAME = null;
let RANK = null;

// helper DOM
const $ = id => document.getElementById(id);
const show = (el) => { el.classList.remove("hidden"); }
const hide = (el) => { el.classList.add("hidden"); }

function setAuthUI(loggedIn){
  if(loggedIn){
    hide($("auth-section"));
    show($("controls-section"));
    $("me-username").innerText = USERNAME;
    $("me-rank").innerText = RANK + " admin";
  } else {
    show($("auth-section"));
    hide($("controls-section"));
  }
}

// login
$("login-btn").addEventListener("click", async () => {
  const username = $("username").value.trim();
  const password = $("password").value.trim();
  $("auth-msg").innerText = "";
  if(!username || !password){ $("auth-msg").innerText = "Enter username & password"; return; }

  const res = await fetch("/api/login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({username, password})
  });
  const data = await res.json();
  if(!data.success){
    $("auth-msg").innerText = data.message || "Login failed";
    return;
  }
  TOKEN = data.token;
  USERNAME = data.username;
  RANK = data.rank;
  setAuthUI(true);
  refreshRooms();
});

// create room
$("create-room-btn").addEventListener("click", async () => {
  const code = $("room-code").value.trim();
  if(!code) return alert("Enter room code");
  const res = await fetch("/api/create_room", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({token:TOKEN, code})
  });
  const data = await res.json();
  if(!data.success){
    alert(data.message || "Could not create");
    return;
  }
  $("room-code").value = "";
  refreshRooms();
});

// change credentials
$("change-cred-btn").addEventListener("click", async () => {
  const new_username = $("new-username").value.trim();
  const new_password = $("new-password").value.trim();
  const res = await fetch("/api/change_credentials", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({token:TOKEN, new_username, new_password})
  });
  const data = await res.json();
  $("cred-msg").innerText = data.message || (data.success ? "Updated" : "Failed");
  if(data.success){
    USERNAME = data.username;
    $("me-username").innerText = USERNAME;
  }
});

// refresh rooms list
$("refresh-rooms").addEventListener("click", refreshRooms);

async function refreshRooms(){
  const res = await fetch("/api/rooms");
  const data = await res.json();
  const container = $("rooms-list");
  container.innerHTML = "";
  if(!data.success) { container.innerHTML = "<p class='muted'>Failed to load</p>"; return; }
  const rooms = data.rooms;
  if(Object.keys(rooms).length === 0){
    container.innerHTML = "<p class='muted'>No rooms yet</p>";
    return;
  }
  Object.entries(rooms).forEach(([code, meta]) => {
    const div = document.createElement("div");
    div.className = "room-item";
    div.innerHTML = `<div><strong>${code}</strong><div class="muted">hosts:${meta.hosts.length} members:${meta.members.length}</div></div>`;
    const btn = document.createElement("button");
    btn.innerText = "Join";
    btn.onclick = () => joinRoom(code);
    div.appendChild(btn);
    container.appendChild(div);
  });
}

// join room via SocketIO
function joinRoom(room){
  if(!TOKEN){ alert("Login first"); return; }
  socket.emit("join", {token:TOKEN, room});
  socket.once("join_response", (resp) => {
    if(!resp.success){ alert(resp.message || "Could not join"); return; }
    CURRENT_ROOM = room;
    $("room-title").innerText = `# ${room}`;
    $("room-meta").innerText = `You: ${USERNAME} • Room: ${room}`;
    $("messages").innerHTML = "";
    show($("chat-input"));
  });
}

// send message
$("send-btn").addEventListener("click", sendMessage);
$("message-text").addEventListener("keydown", (e) => {
  if(e.key === "Enter") sendMessage();
});

function sendMessage(){
  const text = $("message-text").value.trim();
  if(!text || !CURRENT_ROOM) return;
  socket.emit("message", {token:TOKEN, room:CURRENT_ROOM, text});
  $("message-text").value = "";
}

// leave room
$("leave-btn").addEventListener("click", () => {
  if(!CURRENT_ROOM) return;
  socket.emit("leave", {token:TOKEN, room:CURRENT_ROOM});
  appendSystem(`You left ${CURRENT_ROOM}`);
  CURRENT_ROOM = null;
  $("room-title").innerText = "No room selected";
  $("room-meta").innerText = "";
  hide($("chat-input"));
});

// socket events
socket.on("server_msg", d => console.log("server:", d));
socket.on("system", d => appendSystem(d.msg));
socket.on("chat", d => appendChat(d.username, d.text));
socket.on("connect", () => appendSystem("Realtime socket connected"));

function appendSystem(msg){
  const m = document.createElement("div"); m.className = "system"; m.innerText = msg;
  $("messages").appendChild(m); scrollBottom();
}
function appendChat(username, text){
  const m = document.createElement("div"); m.className = "msg";
  if(username === USERNAME) m.classList.add("me");
  m.innerHTML = `<div class="meta">${username}</div><div class="body">${escapeHtml(text)}</div>`;
  $("messages").appendChild(m); scrollBottom();
}
function scrollBottom(){
  const c = $("chat-area");
  c.scrollTop = c.scrollHeight;
}
function escapeHtml(s){ return s.replace(/[&<>"']/g, (c)=>({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" })[c]); }

// initial UI state
setAuthUI(false);
hide($("chat-input"));
refreshRooms();
