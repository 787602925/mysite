document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("chatbot-toggle");
    const container = document.getElementById("chatbot-container");
    const closeBtn = document.getElementById("chatbot-close");
    const sendBtn = document.getElementById("chat-send");
    const input = document.getElementById("chat-input");
    const chatBody = document.getElementById("chat-body");

    // 确保初始状态是隐藏的
    if (container) {
        container.classList.add("chatbot--hidden");
    }

    // 机器人按钮点击事件
    if (toggle) {
        toggle.onclick = () => {
            if (container) {
                container.classList.toggle("chatbot--hidden");
            }
        };
    }
    
    // 关闭按钮点击事件
    if (closeBtn) {
        closeBtn.onclick = () => {
            if (container) {
                container.classList.add("chatbot--hidden");
            }
        };
    }

    const appendMessage = (text, sender) => {
        const div = document.createElement("div");
        div.className = `chatbot__message chatbot__message--${sender}`;
        div.textContent = text;
        chatBody.appendChild(div);
        chatBody.scrollTop = chatBody.scrollHeight;
    };

    const sendMessage = async () => {
        const text = input.value.trim();
        if (!text) return;
        appendMessage(text, "user");
        input.value = "";

        const res = await fetch("/agent/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        });
        const data = await res.json();
        appendMessage(data.reply, "bot");
    };

    // 发送按钮事件
    if (sendBtn) {
        sendBtn.onclick = sendMessage;
    }
    
    // 输入框回车事件
    if (input) {
        input.addEventListener("keypress", e => {
            if (e.key === "Enter") sendMessage();
        });
    }
});
