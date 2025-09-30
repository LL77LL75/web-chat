const ROOM_ADDR = localStorage.getItem("roomAddr");
const USERNAME = localStorage.getItem("username");
const PASSWORD = localStorage.getItem("password");

if (!ROOM_ADDR || !USERNAME || !PASSWORD) {
  alert("Missing data. Please login again.");
  window.location.href = "index.html";
}

document.getElementById("roomTitle").innerText = ROOM_ADDR;

const socket = io(`http://${ROOM_ADDR}`);

const chatBox = document.getElementById("chatBox");
const input = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const leaveBtn = document.getElementById("leaveBtn");

socket.on("connect", () => {
  socket.emit("join", { username: USERNAME, password: PASSWORD });
});

socket.on("history", (messages) => {
  chatBox.innerHTML = "";
  messages.forEach(renderMessage);
  scrollToBottom();
});

socket.on("message", (msg) => {
  renderMessage(msg);
  scrollToBottom();
});

socket.on("edit", (msg) => {
  const el = document.getElementById(msg.id);
  if (el) {
    el.querySelector(".msg-text").innerText = msg.msg;
    el.querySelector(".msg-time").innerText =
      msg.edited ? `${msg.time} (edited ${msg.edited_time})` : msg.time;
  }
});

socket.on("delete", ({ id }) => {
  const el = document.getElementById(id);
  if (el) el.remove();
});

socket.on("sys", (d) => {
  appendSys(d.msg || JSON.stringify(d));
  scrollToBottom();
});

sendBtn.onclick = () => {
  const text = input.value.trim();
  if (!text) return;
  socket.emit("chat", { username: USERNAME, msg: text });
  input.value = "";
};

leaveBtn.onclick = () => {
  socket.emit("leave", { username: USERNAME });
  localStorage.removeItem("roomAddr");
  window.location.href = "dashboard.html";
};

function renderMessage(msg) {
  if (!msg || !msg.id) return;
  if (document.getElementById(msg.id)) return;

  const div = document.createElement("div");
  div.className = "chat-message";
  div.id = msg.id;

  div.innerHTML = `
    <div class="msg-header"><strong>${escapeHtml(msg.user)}</strong></div>
    <div class="msg-body"><span class="msg-text">${escapeHtml(msg.msg)}</span></div>
    <div class="msg-meta"><small class="msg-time">${escapeHtml(msg.time)}${msg.edited ? ` (edited ${escapeHtml(msg.edited_time)})` : ""}</small></div>
  `;

  if (msg.user === USERNAME) {
    const actions = document.createElement("div");
    actions.className = "msg-actions";
    const editBtn = document.createElement("button");
    editBtn.innerText = "Edit";
    editBtn.onclick = () => {
      const newText = prompt("Edit message:", msg.msg);
      if (newText !== null) {
        socket.emit("edit_message", { username: USERNAME, id: msg.id, new: newText });
      }
    };
    const delBtn = document.createElement("button");
    delBtn.innerText = "Delete";
    delBtn.onclick = () => {
      if (confirm("Delete this message?")) {
        socket.emit("delete_message", { username: USERNAME, id: msg.id });
      }
    };
    actions.appendChild(editBtn);
    actions.appendChild(delBtn);
    div.appendChild(actions);
  }

  chatBox.appendChild(div);
}

function appendSys(text) {
  const div = document.createElement("div");
  div.className = "chat-system";
  div.innerHTML = `<em>${escapeHtml(text)}</em>`;
  chatBox.appendChild(div);
}

function scrollToBottom() {
  chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}
