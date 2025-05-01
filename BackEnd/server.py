import asyncio
import base64
import json
import os
import pathlib
from collections.abc import AsyncGenerator
from typing import Literal

import gradio as gr
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastrtc import (
    AsyncStreamHandler,
    Stream,
    get_cloudflare_turn_credentials_async,
    wait_for_item,
)
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    PrebuiltVoiceConfig,
    SpeechConfig,
    VoiceConfig,
    Content,
    Part,
)
from gradio.utils import get_space
from pydantic import BaseModel

# Load environment
current_dir = pathlib.Path(__file__).parent
PROMPT_DIR = current_dir / "prompts"
load_dotenv()

# Prompt cache
_prompt_cache: dict[str, str] = {}

def load_prompt_file(name: str) -> str:
    """Load a prompt file for given character name, with basic validation and fallback."""
    # sanitize name: allow only alphanumeric and underscore
    if not name.isidentifier():
        raise ValueError(f"Invalid character name: {name}")
    prompt_path = PROMPT_DIR / f"{name}.txt"
    if not prompt_path.exists():
        prompt_path = PROMPT_DIR / "default.txt"
        if not prompt_path.exists():
            raise FileNotFoundError("Default prompt not found.")
    return prompt_path.read_text(encoding="utf-8")

def get_prompt(name: str) -> str:
    if name not in _prompt_cache:
        _prompt_cache[name] = load_prompt_file(name)
    return _prompt_cache[name]


def encode_audio(data: np.ndarray) -> str:
    """Encode Audio data to send to the client"""
    return base64.b64encode(data.tobytes()).decode("UTF-8")

class GeminiHandler(AsyncStreamHandler):
    """Handler for the Gemini API with dynamic system_instruction based on character"""

    def __init__(
        self,
        expected_layout: Literal["mono"] = "mono",
        output_sample_rate: int = 24000,
    ) -> None:
        super().__init__(
            expected_layout,
            output_sample_rate,
            input_sample_rate=16000,
        )
        self.input_queue: asyncio.Queue = asyncio.Queue()
        self.output_queue: asyncio.Queue = asyncio.Queue()
        self.quit: asyncio.Event = asyncio.Event()

    def copy(self) -> "GeminiHandler":
        return GeminiHandler(
            expected_layout="mono",
            output_sample_rate=self.output_sample_rate,
        )

    async def start_up(self):
        # Wait for args: [api_key, voice_name, character]
        if not self.phone_mode:
            try:
                await self.wait_for_args()
                api_key, voice_name, character = self.latest_args[1:4]
            except Exception as e:
                raise RuntimeError("Missing initialization arguments") from e
        else:
            api_key, voice_name, character = "AIzaSyB-CXqCqmdcxv-WiaoNKa5mQpHw0n_A_aE", "Puck", "default"

        # Load prompt for character
        try:
            prompt_text = get_prompt(character)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        client = genai.Client(
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            http_options={"api_version": "v1alpha"},
        )

        # Build LiveConnectConfig with dynamic system instruction
        config = LiveConnectConfig(
            system_instruction=Content(
                parts=[Part(text=prompt_text)]
            ),
            response_modalities=["AUDIO"],  # type: ignore
            speech_config=SpeechConfig(
                voice_config=VoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(
                        voice_name=voice_name,
                    )
                )
            ),
        )

        async with client.aio.live.connect(
            model="gemini-2.0-flash-exp", config=config
        ) as session:
            async for audio in session.start_stream(
                stream=self.stream(),
                mime_type="audio/pcm"
            ):
                if audio.data:
                    array = np.frombuffer(audio.data, dtype=np.int16)
                    self.output_queue.put_nowait((self.output_sample_rate, array))

    async def stream(self) -> AsyncGenerator[bytes, None]:
        while not self.quit.is_set():
            try:
                audio = await asyncio.wait_for(self.input_queue.get(), 0.1)
                yield audio
            except (asyncio.TimeoutError, TimeoutError):
                pass

    async def receive(self, frame: tuple[int, np.ndarray]) -> None:
        _, array = frame
        array = array.squeeze()
        audio_message = encode_audio(array)
        self.input_queue.put_nowait(audio_message)

    async def emit(self) -> tuple[int, np.ndarray] | None:
        return await wait_for_item(self.output_queue)

    def shutdown(self) -> None:
        self.quit.set()

# Initialize Stream with dynamic handler
stream = Stream(
    modality="audio",
    mode="send-receive",
    handler=GeminiHandler(),
    rtc_configuration=get_cloudflare_turn_credentials_async,
    concurrency_limit=5,
    time_limit=90 if get_space() else None,
    additional_inputs=[
        gr.Textbox(label="API Key", type="password", value=os.getenv("GEMINI_API_KEY") if not get_space() else ""),
        gr.Dropdown(label="Voice", choices=["Puck","Charon","Kore","Fenrir","Aoede"], value="Puck"),
        gr.Textbox(label="Character", type="text", value="default")  # front-end passes character.id
    ],
)

class InputData(BaseModel):
    webrtc_id: str
    api_key: str
    voice_name: str
    character: str

app = FastAPI()
# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount stream endpoints (/webrtc/offer, etc.)
stream.mount(app)

@app.post("/input_hook")
async def input_hook(body: InputData):
    # Pass all args to the stream handler
    stream.set_input(body.webrtc_id, body.api_key, body.voice_name, body.character)
    return {"status": "ok"}

@app.get("/")
async def index():
    rtc_config = await get_cloudflare_turn_credentials_async() if get_space() else None
    html_content = (current_dir / "index.html").read_text()
    html_content = html_content.replace("__RTC_CONFIGURATION__", json.dumps(rtc_config))
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    mode = os.getenv("MODE")
    if mode == "UI":
        stream.ui.launch(server_port=7860, share=True)
    elif mode == "PHONE":
        stream.fastphone(host="0.0.0.0", port=7860)
    else:
        uvicorn.run(app, host="0.0.0.0", port=7860)


# import asyncio
# import base64
# import json
# import os
# import pathlib
# from collections.abc import AsyncGenerator
# from typing import Literal

# import gradio as gr
# import numpy as np
# from dotenv import load_dotenv
# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse
# from fastrtc import (
#     AsyncStreamHandler,
#     Stream,
#     get_cloudflare_turn_credentials_async,
#     wait_for_item,
# )
# from google import genai
# from google.genai.types import (
#     LiveConnectConfig,
#     PrebuiltVoiceConfig,
#     SpeechConfig,
#     VoiceConfig,
#     Content,
#     Part,
# )
# from gradio.utils import get_space
# from pydantic import BaseModel

# current_dir = pathlib.Path(__file__).parent
# load_dotenv()

# def encode_audio(data: np.ndarray) -> str:
#     """Encode Audio data to send to the server"""
#     return base64.b64encode(data.tobytes()).decode("UTF-8")

# class 
# 
# (AsyncStreamHandler):
#     """Handler for the Gemini API with system_instruction support"""

#     def __init__(
#         self,
#         expected_layout: Literal["mono"] = "mono",
#         output_sample_rate: int = 24000,
#     ) -> None:
#         super().__init__(
#             expected_layout,
#             output_sample_rate,
#             input_sample_rate=16000,
#         )
#         self.input_queue: asyncio.Queue = asyncio.Queue()
#         self.output_queue: asyncio.Queue = asyncio.Queue()
#         self.quit: asyncio.Event = asyncio.Event()

#     def copy(self) -> "GeminiHandler":
#         return GeminiHandler(
#             expected_layout="mono",
#             output_sample_rate=self.output_sample_rate,
#         )

#     async def start_up(self):
#         # retrieve API key and voice name
#         if not self.phone_mode:
#             await self.wait_for_args()
#             api_key, voice_name = self.latest_args[1:]
#         else:
#             api_key, voice_name = None, "Puck"

#         client = genai.Client(
#             api_key=api_key or os.getenv("GEMINI_API_KEY"),
#             http_options={"api_version": "v1alpha"},
#         )

#         # Use system_instruction field in LiveConnectConfig
#         config = LiveConnectConfig(
#             system_instruction=Content(
#                 parts=[Part(text="""
# You are Elon Musk, CEO of SpaceX and Tesla, a visionary engineer and entrepreneur.

# Background:
# - Raised in South Africa; studied physics and economics at UPenn.
# - Founded Zip2, X.com (which became PayPal), SpaceX, Tesla, Neuralink, The Boring Company.

# Personality & Style:
# - Bold, direct, sometimes irreverent; mixes technical depth with big-picture futurism.
# - Uses analogies from physics and engineering to explain complex ideas.
# - Occasionally tweets memes or humorous asides; unafraid of controversy.

# Goals:
# - Speak confidently about space colonization, sustainable energy, AI risks/opportunities.
# - Inspire by painting a compelling vision of humanity as a multi-planetary species.

# When you respond:
# - Adopt Elon’s tone: visionary optimism, technical rigor, playful sarcasm at times.
# - Reference cutting-edge engineering details (rockets, batteries, AI architectures).
# - Keep answers concise but rich in technical insight.
# - Signature style: end with a short, punchy statement of future impact.
# """)]
#             ),
            
#             response_modalities=["AUDIO"],  # type: ignore
#             speech_config=SpeechConfig(
#                 voice_config=VoiceConfig(
#                     prebuilt_voice_config=PrebuiltVoiceConfig(
#                         voice_name=voice_name,
#                     )
#                 )
#             ),
#         )

#         async with client.aio.live.connect(
#             model="gemini-2.0-flash-exp", config=config
#         ) as session:
#             # Stream audio in real-time; system_instruction already applied
#             async for audio in session.start_stream(
#                 stream=self.stream(),
#                 mime_type="audio/pcm"
#             ):
#                 if audio.data:
#                     array = np.frombuffer(audio.data, dtype=np.int16)
#                     self.output_queue.put_nowait((self.output_sample_rate, array))

#     async def stream(self) -> AsyncGenerator[bytes, None]:
#         while not self.quit.is_set():
#             try:
#                 audio = await asyncio.wait_for(self.input_queue.get(), 0.1)
#                 yield audio
#             except (asyncio.TimeoutError, TimeoutError):
#                 pass

#     async def receive(self, frame: tuple[int, np.ndarray]) -> None:
#         _, array = frame
#         array = array.squeeze()
#         audio_message = encode_audio(array)
#         self.input_queue.put_nowait(audio_message)

#     async def emit(self) -> tuple[int, np.ndarray] | None:
#         return await wait_for_item(self.output_queue)

#     def shutdown(self) -> None:
#         self.quit.set()

# # Initialize Stream with our handler
# stream = Stream(
#     modality="audio",
#     mode="send-receive",
#     handler=GeminiHandler(),
#     rtc_configuration=get_cloudflare_turn_credentials_async,
#     concurrency_limit=5,
#     time_limit=90 if get_space() else None,
#     additional_inputs=[
#         gr.Textbox(
#             label="API Key",
#             type="password",
#             value=os.getenv("GEMINI_API_KEY") if not get_space() else "",
#         ),
#         gr.Dropdown(
#             label="Voice",
#             choices=["Puck", "Charon", "Kore", "Fenrir", "Aoede"],
#             value="Puck",
#         ),
#     ],
# )

# class InputData(BaseModel):
#     webrtc_id: str
#     voice_name: str
#     api_key: str

# app = FastAPI()
# # CORS
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Mount stream
# stream.mount(app)

# @app.post("/input_hook")
# async def input_hook(body: InputData):
#     stream.set_input(body.webrtc_id, body.api_key, body.voice_name)
#     return {"status": "ok"}


# @app.get("/")
# async def index():
#     rtc_config = await get_cloudflare_turn_credentials_async() if get_space() else None
#     html_content = (current_dir / "index.html").read_text()
#     html_content = html_content.replace("__RTC_CONFIGURATION__", json.dumps(rtc_config))
#     return HTMLResponse(content=html_content)

# if __name__ == "__main__":
#     import uvicorn
#     mode = os.getenv("MODE")
#     if mode == "UI":
#         stream.ui.launch(server_port=7860, share=True)
#     elif mode == "PHONE":
#         stream.fastphone(host="0.0.0.0", port=7860)
#     else:
#         uvicorn.run(app, host="0.0.0.0", port=7860)

