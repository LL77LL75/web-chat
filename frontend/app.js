// frontend/app.js
// This file is used by index.html, dashboard.html and chat.html.
// It detects current page by elements presence and runs appropriate logic.

const API = "http://localhost:5000"; // adjust if backend hosted elsewhere
let socket = null;
let currentUser = null;
let currentRoom = null;

// helper DOM selectors
const $ = (id) => document.getElementById(id);
const isDashboard = !!$("rooms-list");
const isLogin = !!$("login-btn") && !isDashboard;
const isChat = !!$("chat-area");

// common: load current user from localStorage
function loadUserFromStorage() {
  try {
    currentUser = JSON.parse(localStorage.getItem("chat_user") || "null");
  } catch (e) {
    currentUser = null;
  }
}

// ----------------- LOGIN PAGE -----------------
if (isLogin) {
  loadUserFromStorage();
  // if already logged in, redirect
  if (currentUser) {
    window.location.href = "dashboard.html";
  }

  $("login-btn").addEventListener("click", async () => {
    const username = $("login-username").value.trim();
    const password = $("login-password").value.trim();
    $("login-msg").innerText = "";
    if (!username || !password) { $("login-msg").innerText = "Enter username & password"; return; }

    try {
      const res = await fetch(API + "/login", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({username, password})
      });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        currentUser = { username, rank: data.rank || "member" };
        localStorage.setItem("chat_user", JSON.stringify(currentUser));
        window.location.href = "dashboard.html";
      } else {
        $("login-msg").innerText = data.message || "Invalid credentials";
      }
    } catch (e) {
      $("login-msg").innerText = "Network error";
    }
  });
}

// ----------------- DASHBOARD PAGE -----------------
if (isDashboard) {
  loadUserFromStorage();
  if (!currentUser) {
    window.location.href = "index.html";
  }

  // UI elements
  const roomsList = $("rooms-list");
  const membersList = $("members-list");
  const selectedTitle = $("selected-room-title");
  const joinBtn = $("join-selected-btn");
  const closeRoomBtn = $("close-room-btn");
  const startRoomBtn = $("start-room-btn");
  const createCodeInput = $("create-code");

  let selectedRoom = null;

  $("profile").innerHTML = `<strong>${currentUser.username}</strong><div class="muted">${currentUser.rank}</div>`;

  async function fetchRooms() {
    const res = await fetch(API + "/rooms");
    const data = await res.json();
    return data;
  }

  function renderRooms(rooms) {
    roomsList.innerHTML = "";
    selectedRoom = null;
    selectedTitle.innerText = "Select a room";
    membersList.innerHTML = "<div class='muted'>Select a room to see members</div>";
    joinBtn.disabled = true;
    closeRoomBtn.classList.add("hidden");

    const entries = Object.entries(rooms);
    if (entries.length === 0) {
      roomsList.innerHTML = "<div class='muted'>No rooms yet</div>";
      return;
    }

    for (const [code, meta] of entries) {
      const div = document.createElement("div");
      div.className = "room-item";
      const left = document.createElement("div");
      left.innerHTML = `<strong>${code}</strong><div class="muted">hosts: ${meta.hosts?.length||0} members: ${meta.members?.length||0}</div>`;
      const right = document.createElement("div");
      const btn = document.createElement("button");
      btn.textContent = "Select";
      btn.onclick = () => selectRoom(code);
      right.appendChild(btn);
      div.appendChild(left);
      div.appendChild(right);
      roomsList.appendChild(div);
    }
  }

  async function loadAndRenderRooms() {
    try {
      const rooms = await fetchRooms();
      renderRooms(rooms);
    } catch (e) {
      roomsList.innerHTML = "<div class='muted'>Failed to load rooms</div>";
    }
  }

  async function selectRoom(code) {
    selectedRoom = code;
    selectedTitle.innerText = `Room: ${code}`;
    joinBtn.disabled = false;
    // load members
    const res = await fetch(API + "/room_members", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ code })
    });
    const data = await res.json();
    if (data.status !== "success") {
      membersList.innerHTML = "<div class='muted'>Failed to load members</div>";
      return;
    }
    const members = data.members || [];
    membersList.innerHTML = "";
    if (members.length === 0) {
      membersList.innerHTML = "<div class='muted'>No members</div>";
    }
    members.forEach(m => {
      const div = document.createElement("div");
      div.className = "member-item";
      let label = m.name;
      if (m.muted) label = `${label} (muted)(${m.mute_level})`;
      if (m.banned) label = `${label} (banned)(${m.ban_level})`;
      const left = document.createElement("div");
      left.innerHTML = `<strong>${label}</strong>`;
      const right = document.createElement("div");
      // if admin, show small controls UI placeholders (commands in chat do the real actions)
      if (currentUser.rank === "core" || currentUser.rank === "admin") {
        const info = document.createElement("div"); info.className = "meta";
        info.innerText = `admin view`;
        right.appendChild(info);
      }
      div.appendChild(left);
      div.appendChild(right);
      membersList.appendChild(div);
    });

    // show admin close button if admin
    if (currentUser.rank === "core" || currentUser.rank === "admin") {
      closeRoomBtn.classList.remove("hidden");
    } else {
      closeRoomBtn.classList.add("hidden");
    }
    $("room-actions").classList.remove("hidden");
  }

  joinBtn.addEventListener("click", () => {
    if (!selectedRoom) return;
    // store selected room and navigate to chat
    localStorage.setItem("chat_room", selectedRoom);
    window.location.href = "chat.html";
  });

  $("refresh-btn").addEventListener("click", loadAndRenderRooms);

  // start room button (admin only)
  startRoomBtn.addEventListener("click", async () => {
    if (!(currentUser.rank === "core" || currentUser.rank === "admin")) {
      alert("Only admins can start rooms.");
      return;
    }
    const code = createCodeInput.value.trim();
    if (!code) return alert("Enter a code");
    // ask backend to create room; if exists, return exists
    const res = await fetch(API + "/create_room", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ code, user: currentUser.username })
    });
    const data = await res.json();
    if (data.status === "created") {
      // navigate to new room
      localStorage.setItem("chat_room", code);
      window.location.href = "chat.html";
    } else if (data.status === "exists") {
      // if exists, redirect to existing
      localStorage.setItem("chat_room", code);
      window.location.href = "chat.html";
    } else {
      alert(data.message || "Could not create room");
    }
  });

  // close room (admin)
  closeRoomBtn.addEventListener("click", async () => {
    if (!selectedRoom) return;
    if (!(currentUser.rank === "core" || currentUser.rank === "admin")) {
      alert("Only admins can close rooms.");
      return;
    }
    if (!confirm(`Close room ${selectedRoom}?`)) return;
    const res = await fetch(API + "/shutdown_room", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ code: selectedRoom })
    });
    if (res.ok) {
      await loadAndRenderRooms();
      membersList.innerHTML = "<div class='muted'>Select a room to see members</div>";
      selectedTitle.innerText = "Select a room";
      $("room-actions").classList.add("hidden");
    } else {
      alert("Failed to close room");
    }
  });

  // initial load
  loadAndRenderRooms();
}

// ----------------- CHAT PAGE -----------------
if (isChat) {
  loadUserFromStorage();
  if (!currentUser) window.location.href = "index.html";
  currentRoom = localStorage.getItem("chat_room");
  if (!currentRoom) window.location.href = "dashboard.html";

  $("room-name").innerText = `# ${currentRoom}`;
  const chatArea = $("chat-area");
  const input = $("chat-input");
  const sendBtn = $("send-btn");
  const leaveBtn = $("leave-btn");
  const closeAdminBtn = $("close-room-admin-btn");

  // show admin close room button if admin
  if (currentUser.rank === "core" || currentUser.rank === "admin") {
    closeAdminBtn.classList.remove("hidden");
  }

  // connect socket & identify
  socket = io(API);
  socket.on("connect", () => {
    socket.emit("identify", { username: currentUser.username });
    socket.emit("join", { username: currentUser.username, room: currentRoom });
  });

  socket.on("join_response", (d) => {
    if (!d.success) {
      alert(d.message || "Could not join room");
      window.location.href = "dashboard.html";
      return;
    }
    appendSys(`You joined ${currentRoom}`);
    // refresh members on join
  });

  socket.on("message", (d) => {
    appendMessage(d.user, d.msg);
  });

  socket.on("user_notify", (payload) => {
    // handle private notifications & admin actions
    if (payload.type === "private") {
      appendMessage(`(private) ${payload.from}`, payload.message);
    } else if (payload.type === "private-sent") {
      appendSys(`Private to ${payload.to}: ${payload.message}`);
    } else if (payload.type === "muted") {
      appendSys(`You were muted in ${payload.room} (level ${payload.level})`);
    } else if (payload.type === "banned") {
      appendSys(`You were banned from ${payload.room} (level ${payload.level}). Redirecting to dashboard.`);
      // force leave client-side and redirect
      setTimeout(() => {
        localStorage.removeItem("chat_room");
        window.location.href = "dashboard.html";
      }, 1500);
    } else if (payload.type === "kicked") {
      appendSys(`You were kicked from ${payload.room}. Redirecting to dashboard.`);
      setTimeout(() => {
        localStorage.removeItem("chat_room");
        window.location.href = "dashboard.html";
      }, 1500);
    } else if (payload.type === "private-failed") {
      appendSys(`Private msg failed: ${payload.message}`);
    }
  });

  socket.on("sys", (d) => {
    appendSys(d.msg || JSON.stringify(d));
  });

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });

  leaveBtn.addEventListener("click", () => {
    socket.emit("leave", { username: currentUser.username, room: currentRoom });
    localStorage.removeItem("chat_room");
    window.location.href = "dashboard.html";
  });

  closeAdminBtn.addEventListener("click", async () => {
    if (!(currentUser.rank === "core" || currentUser.rank === "admin")) return;
    if (!confirm("Close this room?")) return;
    await fetch(API + "/shutdown_room", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ code: currentRoom })});
    appendSys("Room closed by admin. Redirecting to dashboard...");
    setTimeout(() => { localStorage.removeItem("chat_room"); window.location.href = "dashboard.html"; }, 1200);
  });

  function appendMessage(user, text) {
    const div = document.createElement("div");
    div.className = "chat-msg";
    div.innerHTML = `<strong>${escapeHtml(user)}:</strong> ${escapeHtml(text)}`;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
  }
  function appendSys(text) {
    const div = document.createElement("div");
    div.className = "chat-msg muted";
    div.innerHTML = `<em>${escapeHtml(text)}</em>`;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, (c)=>({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" })[c]); }

  function sendMessage() {
    const msg = input.value.trim();
    if (!msg) return;
    socket.emit("chat", { username: currentUser.username, room: currentRoom, msg });
    // show message locally if not a command (commands will be echoed by server)
    if (!msg.startsWith("?/")) {
      appendMessage(currentUser.username, msg);
    }
    input.value = "";
  }
}
