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
      <div class="message-bubble">${text}</div>
      <div class="message-time">Just now</div>
    </div>
  `;

  messagesArea.appendChild(messageDiv);
  messageInput.value = "";
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
