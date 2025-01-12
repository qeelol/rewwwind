const chatInput = document.querySelector('.chat-input textarea');
const sendChatBtn = document.querySelector('.chat-input span');
const chatbox = document.querySelector('.chatbox');
const chatbotToggler = document.querySelector('.chatbot-toggler');
const chatbotWrapper = document.querySelector('.chatbot__wrapper');
const chatbotHeaderCloseBtn = document.querySelector('.chatbot header span');
const socket = io();

let currentRoom = null;
let isSupportChat = false;

let userMessage;
let inputInitHeight;

const setInitialHeight = () => {
  inputInitHeight = chatInput.scrollHeight;
};

chatInput.addEventListener("input", () => {
  if (!inputInitHeight) {
    setInitialHeight(); // Set the initial height if not set already
  }
  
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

document.getElementById('supportBtn').addEventListener('click', () => {
  isSupportChat = true;
  document.getElementById('chatChoice').style.display = 'none';
  document.querySelector('.chatbox').style.display = 'block';
  document.querySelector('.chat-input').style.display = 'flex';
  
  // Initialize socket connection for support chat
  initializeSupportChat();
});

document.getElementById('chatbotBtn').addEventListener('click', () => {
  isSupportChat = false;
  document.getElementById('chatChoice').style.display = 'none';
  document.querySelector('.chatbox').style.display = 'block';
  document.querySelector('.chat-input').style.display = 'flex';
});

function initializeSupportChat() {
  // Request customer support
  socket.emit('request_support', {});
  
  // Initial waiting message
  const waitingMessage = createChatLi('Requesting customer support...', 'incoming');
  chatbox.appendChild(waitingMessage);
}

const createChatLi = (message, className) => {
  // create a chat li element with passed message and classname
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", className);

  let chatContent = className === "outgoing" ? `<p></p>` : `<span><i class="fa-solid fa-robot"></i></span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message
  return chatLi;
}

const generateResponse = async (incomingChatLi) => {
  const messageElement = incomingChatLi.querySelector("p");

  try {
    const response = await fetch('/api/chat', { // gemini api endpoint
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector('meta[name="csrf-token"]')?.content
      },
      body: JSON.stringify({
        message: userMessage
      })
    });

    const data = await response.json();
      
    if (response.ok) {
      messageElement.textContent = data.response;
    } else {
      throw new Error(data.error || 'Failed to get response');
    }
  } catch (error) {
    console.error(error);
    messageElement.classList.add("error");
    messageElement.textContent = "Oops! Something went wrong. Please try again.";
  } finally {
    chatbox.scrollTo(0, chatbox.scrollHeight);
  }
}

const handleChat = () => {
  userMessage = chatInput.value.trim();
  // console.log(userMessage)
  if (!userMessage) return;
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px` // revert back to default height once msg sent

  // append user message to chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  if (isSupportChat && currentRoom) {
    // Send message through socket for support chat
    socket.emit('chat_message', {
        room_id: currentRoom,
        message: userMessage
    });
  } else {
    // Original chatbot logic
    setTimeout(() => {
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
  }
}

// resize textarea height based on content
chatInput.addEventListener("input", () => {
  chatInput.style.height = `${inputInitHeight}px`
  chatInput.style.height = `${chatInput.scrollHeight}px`
});

// enter key without shift key and window width > 800
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

chatbotHeaderCloseBtn.addEventListener("click", () => {
  chatbotWrapper.classList.remove("show-chatbot");
});

// floating button actions
chatbotToggler.addEventListener("click", () => {
  chatbotWrapper.classList.toggle("show-chatbot");
});

// Socket event listeners
socket.on('support_request_acknowledged', (data) => {
  currentRoom = data.room_id;
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  chatbox.scrollTo(0, chatbox.scrollHeight);
});

socket.on('admin_joined', (data) => {
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  chatbox.scrollTo(0, chatbox.scrollHeight);
});

socket.on('new_message', (data) => {
  if (data.sender_type !== 'customer') {
    const messageElement = createChatLi(data.message, 'incoming');
    chatbox.appendChild(messageElement);
    chatbox.scrollTo(0, chatbox.scrollHeight);
  }
});

socket.on('chat_ended', (data) => {
  const messageElement = createChatLi(data.message, 'incoming');
  chatbox.appendChild(messageElement);
  chatbox.scrollTo(0, chatbox.scrollHeight);
  currentRoom = null;
  
  // Reset chat interface
  setTimeout(() => {
    document.getElementById('chatChoice').style.display = 'block';
    document.querySelector('.chatbox').style.display = 'none';
    document.querySelector('.chat-input').style.display = 'none';
    chatbox.innerHTML = ''; // Clear chat history
  }, 3000);
});

let connectionInterval;
let lastPong = Date.now();

function startConnectionMonitor() {
  connectionInterval = setInterval(() => {
    // Check if we've received a pong in the last 10 seconds
    if (Date.now() - lastPong > 10000) {
      handleDisconnection();
    }
    socket.emit('ping_connection');
  }, 5000);
}

function handleDisconnection() {
  clearInterval(connectionInterval);
    
  // Show reconnection message
  const messageElement = createChatLi('Connection lost. Attempting to reconnect...', 'system');
  chatbox.appendChild(messageElement);
    
  // Attempt to reconnect
  socket.connect();
}

socket.on('pong_connection', () => {
  lastPong = Date.now();
});

socket.on('connect', () => {
  startConnectionMonitor();
  if (currentRoom) {
    // Rejoin room if we were in one
    socket.emit('rejoin_room', { room_id: currentRoom });
  }
});

socket.on('user_disconnected', (data) => {
  const messageElement = createChatLi(data.message, 'system');
  chatbox.appendChild(messageElement);
    
  if (data.user_type === 'admin') {
    // Reset chat for customer if admin disconnects
    setTimeout(() => {
      resetChat();
    }, 3000);
  }
});

function resetChat() {
  currentRoom = null;
  document.getElementById('chatChoice').style.display = 'block';
  document.querySelector('.chatbox').style.display = 'none';
  document.querySelector('.chat-input').style.display = 'none';
  chatbox.innerHTML = '';
}