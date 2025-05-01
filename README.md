# 🧠 Persona.ai

Persona.ai is a personal AI with a bit of character, built using [LangGraph](https://github.com/langchain-ai/langgraph) that supports **dynamic persona switching**, **Seamless Voice Call**, and a user-friendly **frontend interface with famous Celebrities**. It's designed to deliver a personalized and natural conversational AI friend that's motivates and encourages you.

---

## 🚀 Features

- ✨ **Various Characters:** Easily switch between different personas via LangGraph prompt templates.  
- 🎙️ **Voice Call:** Talk with your AI friend seamless without much waiting  
- 🖥️ **Frontend UI:** Simple and clean interface to chat with your personalized AI assistant.

---
##  Upcoming Features

- **🧠 Memory Database:** It doesn't just chat—it remembers. Your personality, your quirks, your rants... stored locally with RAG-powered recall.
- **💾 Local Storage:** All yours. Nothing goes to the cloud unless you say so.
- **🔓 Uncensored Mode:** No more “I can’t help with that.” Your characters speak their mind—raw, real, and unfiltered.
- **Voice:** Character specific voice with emotions. 

---
## 📌 Goals / Todo

- ✅ **Multi-Character Intelligence:** Integrate diverse personalities into the LangGraph pipeline.
- ✅ **Real-Time Voice Input:** Add instant speech-to-text using the `keyboard` library.
- ✅ **Responsive Frontend:** Smooth, app-like UI built with React & Next.js.
- ✅ **Call UI:** Voice-enabled character calls with WebRTC.

- [ ] **Customizable Characters:** Let users build their own AI personas—name, voice, style, memory.
- [ ] **Uncensored Personalities:** Enable filter-free, boundary-pushing conversations.
- [ ] **Local Brain:** Store long-term memory and chats privately using embedded RAG on-device.

---

## 📁 Project Structure (planned)

```
Persona/
├── FrontEnd/        # Prompt templates & persona definitions
├── BackEnd/
    ├── prompts
    ├── main.py
    ├── server.py
    ├── Lang_Core.py
└── README.md                # Project documentation
```

---

## 🛠️ Tech Stack

- `LangGraph` – For building conversation flows  
- `Gemini / LLM` – Core language model  
- `FastRTC` – Lightweight input capture for Voice Call
- `Next.js| React` – Frontend interface  

---

## 📣 Contributing

Got ideas for fun personas or UX improvements? Feel free to fork, raise issues, or submit PRs! Contributions are welcome.

---

