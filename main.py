# main.py
import os
import pathlib
import json

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import your two existing apps/modules
from Lan_Core import app as chat_app
import server as webrtc_module  # this exposes `stream`, `InputData`, etc.

# Create the “master” app
app = FastAPI(
    title="Persona.ai Combined API",
    description="Mounts both Chat (Lan_Core) and WebRTC (server.py) under one process",
)

# Shared CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

webrtc_module.stream.mount(app)  # mounts fastrtc routes (/webrtc/...)
# re-expose the input_hook route on the master app
@app.post("/input_hook")
async def input_hook(body: webrtc_module.InputData):
    # simply forward into your existing handler
    web_response = webrtc_module.stream.set_input(
        body.webrtc_id, body.api_key, body.voice_name, body.character
    )
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def index():
    # serve the same index.html + RTC config
    current_dir = pathlib.Path(__file__).parent
    rtc_config = await webrtc_module.get_cloudflare_turn_credentials_async()
    html = (current_dir / "index.html").read_text()
    return HTMLResponse(html.replace("__RTC_CONFIGURATION__", json.dumps(rtc_config)))

app.mount("/chat_api", chat_app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
