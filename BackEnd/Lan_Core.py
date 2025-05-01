
# Langgraph Agent with prompt-folder-based system prompts and RunnablePassthrough
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Simple in-memory session memory manager
class MemorySaver:
    def __init__(self):
        self.sessions = {}

    def initialize_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = ""

    def get_session_memory(self, session_id: str) -> str:
        return self.sessions.get(session_id, "")

    def set_session_memory(self, session_id: str, memory: str) -> None:
        self.sessions[session_id] = memory

# 1) Load all character prompts at startup
PROMPT_FOLDER = os.path.join(os.path.dirname(__file__), "prompts")
system_prompts = {}
for fname in os.listdir(PROMPT_FOLDER):
    if fname.endswith(".txt"):
        key = os.path.splitext(fname)[0]
        path = os.path.join(PROMPT_FOLDER, fname)
        with open(path, "r", encoding="utf-8") as f:
            system_prompts[key] = f.read().strip()

# Initialize memory manager and LLM
db_memory = MemorySaver()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key='AIzaSyB-CXqCqmdcxv-WiaoNKa5mQpHw0n_A_aE',
    max_tokens=500,
)

# Helper to retrieve a preloaded prompt or error if missing
def load_system_prompt(character: str) -> str:
    prompt = system_prompts.get(character)
    if not prompt:
        raise FileNotFoundError(f"Prompt file for character '{character}' not found.")
    return prompt

# Core response generator using RunnablePassthrough for chaining
def get_response(session_id: str, user_input: str, character: str) -> str:
    # Ensure session
    db_memory.initialize_session(session_id)
    history = db_memory.get_session_memory(session_id)

    # System prompt seed on first turn
    system_prompt = load_system_prompt(character)
    if not history:
        history = f"System: {system_prompt}\n"

    # Build dynamic prompt template
    local_prompt_template = PromptTemplate(
        input_variables=["history", "user_input"],
        template="{history}User: {user_input}\n" + f"{character}:",
    )

    # Chain: template -> LLM -> passthrough (no internal memory changes)
    local_chain = local_prompt_template | llm | RunnablePassthrough()

    # Invoke chain and extract text
    chain_input = {"history": history, "user_input": user_input}
    resp = local_chain.invoke(chain_input)
    response_text = getattr(resp, "content", str(resp)).strip()

    # Update session memory
    new_history = history + f"User: {user_input}\n{character}: {response_text}\n"
    db_memory.set_session_memory(session_id, new_history)

    return response_text

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and response schemas
class ChatRequest(BaseModel):
    session_id: str
    user_input: str
    character: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        resp_text = get_response(
            session_id=request.session_id,
            user_input=request.user_input,
            character=request.character,
        )
        return ChatResponse(response=resp_text)
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional CLI testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
