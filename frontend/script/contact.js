const socket = io("http://127.0.0.1:8000", {
  transports: ["websocket"],
  withCredentials: true,
});

const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messagesArea = document.getElementById("messagesArea");

function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) return;

  const messageDiv = document.createElement("div");
  messageDiv.className = "message sent";
  messageDiv.innerHTML = `
    <div class="message-content">
      <div class="message-time">${text}</div>
      <div class="message-time">${new Date().toLocaleTimeString()}</div>
    </div>
  `;

  messagesArea.appendChild(messageDiv);
  messageInput.value = "";
  messagesArea.scrollTop = messagesArea.scrollHeight;

  socket.emit("send_message", { room: ROOM_CODE, message: text });
}

function receiveMessage(text, timeNow, senderRole, senderInitial) {
  if (!text) return;

  const messageDiv = document.createElement("div");
  messageDiv.className = senderRole === "hoster" ? "message received" : "message sent";

  messageDiv.innerHTML = `
    <div class="message-avatar">${senderInitial}</div>
    <div class="message-content">
      <div class="message-bubble">${text}</div>
      <div class="message-time">${timeNow}</div>
    </div>
  `;

  messagesArea.appendChild(messageDiv);
  messagesArea.scrollTop = messagesArea.scrollHeight;
}


sendBtn.addEventListener("click", sendMessage);

messageInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});

document.querySelectorAll(".conversation-item").forEach((item) => {
  item.addEventListener("click", () => {
    document
      .querySelectorAll(".conversation-item")
      .forEach((i) => i.classList.remove("active"));
    item.classList.add("active");
  });
});

console.log(ROOM_CODE);

socket.on("connect", () => {
  console.log("socket connected:", socket.id);
  socket.emit("join_room", { room: ROOM_CODE });
});

socket.on("joined_room", (data) => {
  console.log("Successfully joined room:", data.room);
});

socket.on("error_message", (data) => {
  console.error("Error:", data.message);
});

socket.on("receive_message", (data) => {
  const senderInitial = data.sender_name ? data.sender_name[0].toUpperCase() : "?";
  receiveMessage(data.message, data.timestamp, data.sender_role, senderInitial);
});


