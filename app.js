const socket = io("http://localhost:5000");

let username = sessionStorage.getItem("username");
let room = sessionStorage.getItem("room");

socket.emit("join", { username, room });

// --- Receive history ---
socket.on("history", (messages) => {
  messages.forEach(renderMessage);
});

// --- New messages ---
socket.on("message", (msg) => {
  renderMessage(msg);
});

// --- Delete ---
socket.on("delete", ({ id }) => {
  document.getElementById(id)?.remove();
});

// --- Edit ---
socket.on("edit", (msg) => {
  let el = document.getElementById(msg.id);
  if (el) {
    el.querySelector(".text").innerText = msg.msg;
    let meta = msg.edited
      ? `${msg.time}, edited ${msg.edited_time}`
      : msg.time;
    el.querySelector(".time").innerText = meta;
  }
});

function sendMessage() {
  let input = document.getElementById("message");
  let text = input.value.trim();
  if (!text) return;
  socket.emit("chat", { username, room, msg: text });
  input.value = "";
}

function renderMessage(msg) {
  let box = document.getElementById("chat-box");
  let div = document.createElement("div");
  div.id = msg.id;

  let canEdit = msg.user === username;

  div.innerHTML = `
    <strong>${msg.user}:</strong>
    <span class="text">${msg.msg}</span>
    <small class="time">${msg.time}${
    msg.edited ? `, edited ${msg.edited_time}` : ""
  }</small>
    ${canEdit ? `<button onclick="deleteMsg('${msg.id}')">❌</button>` : ""}
    ${canEdit ? `<button onclick="editMsg('${msg.id}')">✏️</button>` : ""}
  `;
  box.appendChild(div);
}

function deleteMsg(id) {
  socket.emit("delete_message", { username, room, id });
}

function editMsg(id) {
  let newText = prompt("Edit message:");
  if (newText) {
    socket.emit("edit_message", { username, room, id, new: newText });
  }
}
