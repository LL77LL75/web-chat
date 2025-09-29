const API_URL = "http://localhost:5000";
let currentUser = null;
let currentRoom = null;
let socket = null;

// Login
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("loginForm")) {
    document.getElementById("loginForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      let username = document.getElementById("username").value;
      let password = document.getElementById("password").value;

      let res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      let data = await res.json();

      if (data.status === "success") {
        currentUser = { username, rank: data.rank };
        localStorage.setItem("user", JSON.stringify(currentUser));
        window.location.href = "dashboard.html";
      } else {
        document.getElementById("loginMsg").textContent = "❌ Invalid credentials!";
      }
    });
  }

  // Dashboard
  if (document.getElementById("roomList")) {
    currentUser = JSON.parse(localStorage.getItem("user"));
    document.getElementById("welcome").textContent = `Welcome, ${currentUser.username} (${currentUser.rank} admin)`;
    loadRooms();
  }

  // Chat
  if (document.getElementById("messages")) {
    currentUser = JSON.parse(localStorage.getItem("user"));
    currentRoom = localStorage.getItem("room");

    document.getElementById("roomName").textContent = `💬 Room: ${currentRoom}`;
    socket = io(API_URL);

    socket.emit("join", { username: currentUser.username, room: currentRoom });

    socket.on("message", (data) => {
      let messages = document.getElementById("messages");
      let div = document.createElement("div");
      div.textContent = `${data.user}: ${data.msg}`;
      messages.appendChild(div);
    });
  }
});

// Room management
async function loadRooms() {
  let res = await fetch(`${API_URL}/rooms`);
  let rooms = await res.json();
  let list = document.getElementById("roomList");
  list.innerHTML = "";
  for (let code in rooms) {
    let li = document.createElement("li");
    li.textContent = `Code: ${code}, Hosts: ${rooms[code].hosts.length}, Members: ${rooms[code].members.length}`;
    list.appendChild(li);
  }
}

async function createRoom() {
  let code = document.getElementById("roomCode").value;
  if (!code) return;
  await fetch(`${API_URL}/create_room`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, user: currentUser.username })
  });
  loadRooms();
}

async function joinRoom() {
  let code = document.getElementById("roomCode").value;
  if (!code) return;
  localStorage.setItem("room", code);
  window.location.href = "chat.html";
}

async function shutdownRoom() {
  let code = document.getElementById("roomCode").value;
  if (!code) return;
  await fetch(`${API_URL}/shutdown_room`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code })
  });
  loadRooms();
}

// Chat
function sendMessage() {
  let input = document.getElementById("chatInput");
  let msg = input.value.trim();
  if (!msg) return;
  socket.emit("chat", { username: currentUser.username, msg, room: currentRoom });
  input.value = "";
}

function leaveRoom() {
  socket.emit("leave", { username: currentUser.username, room: currentRoom });
  localStorage.removeItem("room");
  window.location.href = "dashboard.html";
}
