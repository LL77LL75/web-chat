document.getElementById("joinBtn").onclick = () => {
  const addr = document.getElementById("roomAddr").value.trim();
  if (!addr) {
    alert("Enter room address");
    return;
  }
  localStorage.setItem("roomAddr", addr);
  window.location.href = "room.html";
};
