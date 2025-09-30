document.getElementById("loginBtn").onclick = () => {
  const user = document.getElementById("username").value.trim();
  const pwd = document.getElementById("password").value.trim();
  if (!user || !pwd) {
    alert("Enter both username and password");
    return;
  }
  localStorage.setItem("username", user);
  localStorage.setItem("password", pwd);
  window.location.href = "dashboard.html";
};
