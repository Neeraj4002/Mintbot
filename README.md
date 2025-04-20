# 🧠 Mintbot

Mintbot is an interactive AI assistant built using [LangGraph](https://github.com/langchain-ai/langgraph) that supports **dynamic persona switching**, **speech-to-text input**, and a user-friendly **frontend interface**. It's designed to deliver a personalized and natural conversational experience.

---

## 🚀 Features

- ✨ **Dynamic Characters:** Easily switch between different personas via LangGraph prompt templates.  
- 🎙️ **Voice Input:** Use the `keyboard` library to capture speech-to-text input for a hands-free experience.
- 🔊**Voice Output:** Use `OpenVoice` to clone character voices like Elon Musk or anime girl etc
- 🖥️ **Frontend UI:** Simple and clean interface to chat with your personalized AI assistant.

---

## 📌 Goals / Todo

- [ ] Integrate multiple character personalities into the LangGraph template.  
- [ ] Add real-time speech-to-text functionality using the `keyboard` library.  
- [ ] Build a responsive frontend for seamless interaction.

---

## 📁 Project Structure (planned)

```
mintbot/
├── langgraph_config/        # Prompt templates & persona definitions
├── stt/             # STT handling using keyboard/microphone
├── frontend/                # Web interface (Streamlit/Next.js/etc.)
├── main.py                  # Entry point for launching the bot
└── README.md                # Project documentation
```

---

## 🛠️ Tech Stack

- `LangGraph` – For building conversation flows  
- `Gemini / LLM` – Core language model  
- `keyboard` – Lightweight input capture for STT
- `OpenVoice TTS` - A voice clonning TTS
- `Streamlit` or `Next.js` – Frontend interface  

---

## 📣 Contributing

Got ideas for fun personas or UX improvements? Feel free to fork, raise issues, or submit PRs! Contributions are welcome.

---

