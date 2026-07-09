const chatList = document.getElementById("chat-list");
const knowledgeContainer = document.getElementById("knowledge-container");
const statusConnection = document.getElementById("status-connection");
const statusTopics = document.getElementById("status-topics");
const statusTopK = document.getElementById("status-topk");
const statusModel = document.getElementById("status-model");
const errorBanner = document.getElementById("error-banner");
const form = document.getElementById("chat-form");
const input = document.getElementById("question-input");
const suggestionButtons = document.querySelectorAll(".pill-button");
const sendButton = document.getElementById("send-button");

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.classList.remove("hidden");
  setTimeout(() => errorBanner.classList.add("hidden"), 5000);
}

function appendMessage(role, content) {

    const message = document.createElement("div");
    message.className = `message ${role}`;

    if (role === "assistant") {

        message.innerHTML = `
            <div class="assistant-title">🤖 OKAI</div>
            <div class="assistant-response">
                ${marked.parse(content)}
            </div>
        `;

    } else {

        message.textContent = content;

    }

    chatList.appendChild(message);
    chatList.scrollTop = chatList.scrollHeight;
}


function setLoading(isLoading) {
  sendButton.textContent = isLoading ? "Thinking..." : "Send";
  sendButton.disabled = isLoading;
  input.disabled = isLoading;
}

function renderKnowledge(items) {
  knowledgeContainer.innerHTML = "";
  if (!items || items.length === 0) {
    knowledgeContainer.innerHTML = '<p class="empty-state">No knowledge results were retrieved.</p>';
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "knowledge-card";
    card.innerHTML = `
      <h4>${item.rank}. ${item.topic}</h4>
      <p>${item.summary || "No summary available."}</p>
      <div class="meta">
        <span>Module: ${item.module || "N/A"}</span>
        <span>Score: ${item.score}</span>
      </div>
      ${item.navigation && item.navigation.length ? `<p><strong>Navigation:</strong> ${item.navigation.join(", ")}</p>` : ""}
    `;
    knowledgeContainer.appendChild(card);
  });
}

async function loadStatus() {
  try {
    const response = await fetch("/api/status");
    if (!response.ok) {
      throw new Error("Unable to load status.");
    }
    const data = await response.json();
    statusConnection.textContent = "Ready";
    statusTopics.textContent = data.knowledgeTopics;
    statusTopK.textContent = data.topK;
    statusModel.textContent = data.model;
  } catch (error) {
    statusConnection.textContent = "Offline";
    showError("Could not connect to the OKAI backend.");
  }
}

async function askQuestion(question) {
  if (!question.trim()) {
    showError("Please type a question before sending.");
    return;
  }

  appendMessage("user", question);
  setLoading(true);
  input.value = "";
  knowledgeContainer.innerHTML = "";

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const errorBody = await response.json();
      throw new Error(errorBody.detail || "There was an issue sending your request.");
    }

    const result = await response.json();
    appendMessage("assistant", result.answer);
    renderKnowledge(result.knowledge);
  } catch (error) {
    appendMessage("assistant", "Sorry, something went wrong while retrieving the answer.");
    showError(error.message);
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  askQuestion(input.value);
});

suggestionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    askQuestion(button.dataset.suggestion);
  });
});

window.addEventListener("DOMContentLoaded", () => {
  loadStatus();
});
