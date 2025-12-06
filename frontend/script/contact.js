// Debug: Check all cookies
console.log("Room code:", ROOM_CODE);
console.log("Current cookies:", document.cookie);

// Socket.IO connection with proper settings for HttpOnly cookies
const socket = io({
  path: "/socket.io/",
  transports: ["polling", "websocket"],
  withCredentials: true,
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5
});

const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messagesArea = document.getElementById("messagesArea");

function sendMessage() {
  const text = messageInput.value.trim();
  if (!text || !ROOM_CODE) {
    console.log('No message or room code');
    return;
  }
  
  console.log('Sending message:', text, 'to room:', ROOM_CODE);
  
  // Send via socket - the receive_message event will handle displaying it
  socket.emit("send_message", { room: ROOM_CODE, message: text });
  
  messageInput.value = "";
}

function receiveMessage(text, timeNow, senderRole, senderInitial) {
  if (!text) return;
  
  const messageDiv = document.createElement("div");
  messageDiv.className = senderRole === "hoster" ? "message received" : "message sent";
  
  // Only show avatar for received messages
  if (senderRole === "hoster") {
    messageDiv.innerHTML = `
      <div class="message-avatar">${senderInitial}</div>
      <div class="message-content">
        <div class="message-bubble">${text}</div>
        <div class="message-time">${timeNow}</div>
      </div>
    `;
  } else {
    messageDiv.innerHTML = `
      <div class="message-content">
        <div class="message-bubble">${text}</div>
        <div class="message-time">${timeNow}</div>
      </div>
    `;
  }
  
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

document.querySelectorAll('.conversation-item').forEach(item => {
  item.addEventListener('click', function() {

    document.querySelectorAll('.conversation-item').forEach(i => 
      i.classList.remove('active')
    );
    
    this.classList.add('active');
    
    const roomCode = this.dataset.room;
    console.log('Switching to room:', roomCode);
    
    window.location.href = `/contact/${roomCode}`;
  });
});

