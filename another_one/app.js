let ws;
let currentUser = null;
let currentRoom = null;

// On login
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("loginForm")) {
    document.getElementById("loginForm").addEventListener("submit", (e) => {
      e.preventDefault();
      let username = document.getElementById("username").value;
      currentUser = username;
      localStorage.setItem("user", username);
      window.location.href = "dashboard.html";
    });
  }

  if (document.getElementById("roomList")) {
    currentUser = localStorage.getItem("user");
    document.getElementById("welcome").textContent = `Welcome, ${currentUser}`;
  }

  if (document.getElementById("messages")) {
    currentUser = localStorage.getItem("user");
    currentRoom = localStorage.getItem("room");
    document.getElementById("roomName").textContent = `💬 Room: ${currentRoom}`;
    connectWebSocket();
  }
});

// Connect WebSocket
function connectWebSocket() {
  ws = new WebSocket("ws://localhost:8765");

  ws.onopen = () => {
    ws.send(JSON.stringify({ type: "register", username: currentUser }));
    ws.send(JSON.stringify({ type: "join", room: currentRoom }));
  };

  ws.onmessage = (event) => {
    let data = JSON.parse(event.data);
    let messages = document.getElementById("messages");

    if (data.type === "system") {
      let div = document.createElement("div");
      div.textContent = `⚙️ ${data.msg}`;
      messages.appendChild(div);
    }

    if (data.type === "chat") {
      let div = document.createElement("div");
      div.textContent = `${data.user}: ${data.msg}`;
      messages.appendChild(div);
    }
  };
}

// Join Room
function joinRoom() {
  let code = document.getElementById("roomCode").value;
  if (!code) return;
  localStorage.setItem("room", code);
  window.location.href = "chat.html";
}

// Chat
function sendMessage() {
  let input = document.getElementById("chatInput");
  let msg = input.value.trim();
  if (!msg) return;
  ws.send(JSON.stringify({ type: "chat", room: currentRoom, msg }));
  input.value = "";
}

// Leave Room
function leaveRoom() {
  localStorage.removeItem("room");
  window.location.href = "dashboard.html";
}
