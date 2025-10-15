const users = [];
const rooms = [
  { id: 'room1', name: 'General Chat', users: [], messages: [] },
  { id: 'room2', name: 'Tech Talk', users: [], messages: [] },
  { id: 'room3', name: 'Gaming Zone', users: [], messages: [] }
];
let currentUser = null;
let currentRoom = null;

document.getElementById('login-btn').addEventListener('click', () => {
  const username = document.getElementById('username').value;
  if (username) {
    currentUser = { username, role: 'member' };
    users.push(currentUser);
    showRoomSelection();
  }
});

function showRoomSelection() {
  document.getElementById('login-screen').classList.add('hidden');
  document.getElementById('room-selection').classList.remove('hidden');
  const roomsList = document.getElementById('rooms-list');
  roomsList.innerHTML = '';
  rooms.forEach(room => {
    const roomButton = document.createElement('button');
    roomButton.textContent = room.name;
    roomButton.addEventListener('click', () => joinRoom(room));
    roomsList.appendChild(roomButton);
  });
}

function joinRoom(room) {
  currentRoom = room;
  room.users.push(currentUser);
  showChatInterface();
}

function showChatInterface() {
  document.getElementById('room-selection').classList.add('hidden');
  document.getElementById('chat-interface').classList.remove('hidden');
  document.getElementById('room-name').textContent = currentRoom.name;
  updateChatArea();
  updateUserList();
}

function updateChatArea() {
  const chatArea = document.getElementById('chat-area');
  chatArea.innerHTML = '';
  currentRoom.messages.forEach(msg => {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = `${msg.sender}: ${msg.text}`;
    chatArea.appendChild(messageDiv);
  });
}

function updateUserList() {
  const userList = document.getElementById('user-list');
  userList.innerHTML = '';
  currentRoom.users.forEach(user => {
    const userDiv = document.createElement('div');
    userDiv.textContent = user.username;
    userList.appendChild(userDiv);
  });
}

document.getElementById('send-btn').addEventListener('click', () => {
  const messageText = document.getElementById('message-text').value;
  if (messageText) {
    currentRoom.messages.push({ sender: currentUser.username, text: messageText });
    updateChatArea();
  }
});

document.getElementById('logout-btn').addEventListener('click', () => {
  currentUser = null;
  currentRoom = null;
  document.getElementById('chat-interface').classList.add('hidden');
  document.getElementById('login-screen').classList.remove('hidden');
});
