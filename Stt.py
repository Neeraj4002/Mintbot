import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import time

class STTModule:
    def __init__(
        self,
        model_size: str = "small", 
        device: str = "cpu", 
        compute_type: str = "int8",
        beam_size: int = 5
    ):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        self.beam_size = beam_size

    def transcribe_bytes(self, audio_bytes: bytes, sampling_rate: int = 16000) -> str:
        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        segments, _ = self.model.transcribe(audio, beam_size=self.beam_size)
        return "".join(seg.text for seg in segments)

    def record_and_transcribe(
        self,
        duration: float = 20.0,
        silence_duration: float = 5.0,
        silence_threshold: int = 500,
        sampling_rate: int = 16000,
    ):
        frame_duration = 0.5  # seconds per frame
        frame_samples = int(frame_duration * sampling_rate)
        silence_frames = int(silence_duration / frame_duration)

        recorded_frames = []
        silence_counter = 0
        stop_event = threading.Event()
        start_time = time.time()

        def record_audio():
            nonlocal recorded_frames, silence_counter
            with sd.InputStream(samplerate=sampling_rate, channels=1, dtype='int16') as stream:
                print(f"🔴 Recording... (Auto-stop after {silence_duration}s silence or {duration}s max)")
                while not stop_event.is_set():
                    frame, _ = stream.read(frame_samples)
                    recorded_frames.append(frame.copy())

                    # Silence check
                    if np.max(np.abs(frame)) < silence_threshold:
                        silence_counter += 1
                    else:
                        silence_counter = 0

                    if silence_counter >= silence_frames or (time.time() - start_time) >= duration:
                        stop_event.set()
        
        Text = ""  # Initialize Text in the enclosing scope

        def transcribe_audio():
            nonlocal recorded_frames, Text
            while not stop_event.is_set() or len(recorded_frames) > 0:
                if len(recorded_frames) > 0:
                    chunk = np.concatenate(recorded_frames, axis=0)
                    recorded_frames = []  # clear buffer
                    audio_bytes = chunk.flatten().tobytes()
                    text = self.transcribe_bytes(audio_bytes, sampling_rate=sampling_rate)
                    print(f"Transcription: {text}")
                    Text += text

        # Start threads
        recording_thread = threading.Thread(target=record_audio)
        transcription_thread = threading.Thread(target=transcribe_audio)

        recording_thread.start()
        transcription_thread.start()

        stop_event.wait()
        recording_thread.join()
        transcription_thread.join()

        print("✅ Recording stopped.")
        print(Text)

# Run it
if __name__ == "__main__":
    stt = STTModule()
    print("🎙️ Start speaking...")
    stt.record_and_transcribe(duration=60, silence_duration=5, silence_threshold=500)


# # stt_module 5 [Worked well but fixed 20 sec duration].py

# """
# Speech-to-Text (STT) module using Faster Whisper optimized for 10–20 s utterances.
# Requires: Python 3.12+, faster-whisper, sounddevice, numpy
# """

# import numpy as np
# from faster_whisper import WhisperModel
# import sounddevice as sd

# class STTModule:
#     """
#     STTModule provides methods to record short (<=20s) audio clips,
#     auto-stopping on silence, and transcribe them with low latency on CPU.

#     Usage:
#         stt = STTModule()
#         # Record until 5s silence or max 20s, then transcribe
#         text = stt.record_and_transcribe(duration=20, silence_duration=5)
#         print(text)
#     """

#     def __init__(
#         self,
#         model_size: str = "small",
#         device: str = "cpu",
#         compute_type: str = "int8",
#         beam_size: int = 5
#     ):
#         """
#         Initialize the Faster Whisper model with CPU-friendly quantization.

#         Args:
#             model_size: Whisper model size ("tiny","base","small").
#             device: "cpu" or "cuda".
#             compute_type: "int8" for fastest CPU inference.
#             beam_size: decoding beam size for accuracy.
#         """
#         self.model = WhisperModel(
#             model_size,
#             device=device,
#             compute_type=compute_type
#         )
#         self.beam_size = beam_size

#     def transcribe_bytes(
#         self,
#         audio_bytes: bytes,
#         sampling_rate: int = 16000,
#         **kwargs
#     ) -> str:
#         """
#         Transcribe raw 16-bit PCM audio bytes (mono) to text.

#         Args:
#             audio_bytes: byte string from sounddevice recording.
#             sampling_rate: sample rate used to record.
#             **kwargs: extra WhisperModel.transcribe parameters (language, task).
#         Returns:
#             Full transcription string.
#         """
#         # normalize int16 PCM to float32 waveform
#         audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#         segments, _ = self.model.transcribe(
#             audio,
            
#             beam_size=self.beam_size,
#             **kwargs
#         )
#         return "".join(seg.text for seg in segments)

#     def record_and_transcribe(
#         self,
#         duration: float = 20.0,
#         sampling_rate: int = 16000,
#         silence_duration: float = 5.0,
#         silence_threshold: int = 500,
#         **kwargs
#     ) -> str:
#         """
#         Record audio from the default microphone until silence is detected
#         for a given duration or until max duration is reached, then transcribe.

#         Args:
#             duration: max recording duration in seconds (<=20).
#             sampling_rate: mic sample rate.
#             silence_duration: seconds of continuous silence to auto-stop.
#             silence_threshold: amplitude threshold for silence (int16).
#             **kwargs: extra transcription options.

#         Returns:
#             Transcribed text.
#         """
#         if duration > 20.0:
#             raise ValueError("Duration exceeds 20 seconds for optimal latency.")

#         frame_duration = 0.5  # seconds per frame
#         frame_samples = int(frame_duration * sampling_rate)
#         max_frames = int(duration / frame_duration)
#         max_silence_frames = int(silence_duration / frame_duration)

#         print(f"🔴 Recording (auto-stop after {silence_duration}s silence or {duration}s max)...")
#         recorded_frames = []
#         silence_frames = 0

#         with sd.InputStream(samplerate=sampling_rate, channels=1, dtype='int16') as stream:
#             for i in range(max_frames):
#                 frame, _ = stream.read(frame_samples)
#                 recorded_frames.append(frame.copy())
#                 # check silence based on absolute amplitude
#                 if np.max(np.abs(frame)) < silence_threshold:
#                     silence_frames += 1
#                 else:
#                     silence_frames = 0
#                 if silence_frames >= max_silence_frames:
#                     print(f"⏹️ Stopped: {silence_duration}s of silence detected.")
#                     break

#         # concatenate frames and transcribe
#         audio = np.concatenate(recorded_frames, axis=0)
#         audio_bytes = audio.flatten().tobytes()
#         print("Transcribing...")
#         return self.transcribe_bytes(audio_bytes, sampling_rate=sampling_rate, **kwargs)


# stt = STTModule()
# # Record until 5s silence or 15s max
# text = stt.record_and_transcribe(duration=15, silence_duration=5, silence_threshold=500)
# print(text)


# # stt_module.py

# """
# Speech-to-Text (STT) module using Faster Whisper (CTranslate2)
# Requires: Python 3.12+, faster-whisper, sounddevice, numpy
# """

# import numpy as np
# from faster_whisper import WhisperModel
# import sounddevice as sd
# import soundfile as sf
# import math
# import asyncio

# class STTModule:
#     """
#     STTModule wraps the Faster Whisper model for file-based and streaming transcription.

#     Example:
#         stt = STTModule(
#             model_size="small",
#             device="cpu",
#             compute_type="int8",
#             beam_size=5
#         )
#         await stt.start_realtime_transcription()
#     """

#     def __init__(
#         self,
#         model_size: str = "small",
#         device: str = "cpu",
#         compute_type: str = "int8",
#         beam_size: int = 5
#     ):
#         self.model = WhisperModel(
#             model_size,
#             device=device,
#             compute_type=compute_type
#         )
#         self.beam_size = beam_size
#     Transcription = " "
#     def transcribe_file(self, file_path: str, **kwargs) -> str:
#         segments, _ = self.model.transcribe(
#             file_path,
#             beam_size=self.beam_size,
#             **kwargs
#         )
#         return "".join([seg.text for seg in segments])

#     def transcribe_bytes(
#         self,
#         audio_bytes: bytes,
#         sampling_rate: int = 16000,
#         **kwargs
#     ) -> str:
#         audio = (
#             np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#         )
#         segments, _ = self.model.transcribe(
#             audio,
#             beam_size=self.beam_size,
#             **kwargs
#         )
#         return "".join([seg.text for seg in segments])

#     async def transcribe_stream(
#         self,
#         chunk_duration: float = 3.0,
#         sampling_rate: int = 16000,
#         **kwargs
#     ):
#         loop = asyncio.get_event_loop()
#         stream = sd.InputStream(
#             samplerate=sampling_rate,
#             channels=1,
#             dtype="int16"
#         )
#         stream.start()
#         try:
#             while True:
#                 data, _ = await loop.run_in_executor(
#                     None,
#                     stream.read,
#                     int(chunk_duration * sampling_rate)
#                 )
#                 audio_bytes = data.flatten().tobytes()
#                 yield self.transcribe_bytes(
#                     audio_bytes,
#                     sampling_rate=sampling_rate,
#                     **kwargs
#                 )
#         finally:
#             stream.stop()
#             stream.close()

#     async def start_realtime_transcription(
#         self,
#         chunk_duration: float = 3.0,
#         sampling_rate: int = 16000,
#         **kwargs
#     ):
#         """
#         Continuously transcribes audio from microphone in real-time and prints it.
#         """
#         print("\n🔴 Real-time transcription started. Speak into your mic...")
#         try:
#             async for text in self.transcribe_stream(
#                 chunk_duration=chunk_duration,
#                 sampling_rate=sampling_rate,
#                 **kwargs
#             ):
#                 print(f"🗣️ {text}")
#                 self.Transcription += text + " "
#                 # Optionally, save the transcription to a file or process it further
#         except KeyboardInterrupt:
#             print("\n🛑 Transcription stopped.")
#             print("You said:", self.Transcription)

#     def record_and_transcribe(
#         self,
#         duration: float = 5.0,
#         chunk_size: float = 20.0,
#         sampling_rate: int = 16000,
#         print_live: bool = True,
#         **kwargs
#     ) -> str:
#         """
#         Records audio from the microphone and returns transcription.
#         Automatically splits long recordings into chunks for better performance.

#         Args:
#             duration: Total recording duration in seconds.
#             chunk_size: How long each chunk should be (in seconds).
#             sampling_rate: Sample rate for recording.
#             print_live: If True, prints each chunk's transcription as it's processed.
#             **kwargs: Additional parameters for transcription.

#         Returns:
#             Full transcription.
#         """
#         print(f"Recording for {duration} seconds...")
#         recording = sd.rec(
#             int(duration * sampling_rate),
#             samplerate=sampling_rate,
#             channels=1,
#             dtype='int16'
#         )
#         sd.wait()
#         print("Recording complete. Transcribing in chunks...")

#         total_samples = int(duration * sampling_rate)
#         chunk_samples = int(chunk_size * sampling_rate)
#         full_text = ""

#         for i in range(0, total_samples, chunk_samples):
#             chunk = recording[i:i + chunk_samples]
#             audio_bytes = chunk.flatten().tobytes()
#             text = self.transcribe_bytes(audio_bytes, sampling_rate=sampling_rate, **kwargs)
#             if print_live:
#                 print(f"[Chunk {i // chunk_samples + 1}] {text}")
#             full_text += text + " "

#         return full_text.strip()
# import asyncio

# stt = STTModule(
#     model_size="small",
#     device="cpu",
#     compute_type="int8",
#     beam_size=5
# )
# asyncio.run(stt.start_realtime_transcription())


# # stt_module 3.py

# """
# Speech-to-Text (STT) module using Faster Whisper (CTranslate2)
# Requires: Python 3.12+, faster-whisper, sounddevice, numpy
# """

# import numpy as np
# from faster_whisper import WhisperModel
# import sounddevice as sd
# import soundfile as sf
# import math

# class STTModule:
#     """
#     STTModule wraps the Faster Whisper model for file-based and streaming transcription.

#     Example:
#         stt = STTModule(
#             model_size="small",
#             device="cpu",
#             compute_type="int8",
#             beam_size=5
#         )
#         text = stt.record_and_transcribe(duration=5)
#         print(text)
#     """

#     def __init__(
#         self,
#         model_size: str = "small",
#         device: str = "cpu",
#         compute_type: str = "int8",
#         beam_size: int = 5
#     ):
#         self.model = WhisperModel(
#             model_size,
#             device=device,
#             compute_type=compute_type
#         )
#         self.beam_size = beam_size

#     def transcribe_file(self, file_path: str, **kwargs) -> str:
#         segments, _ = self.model.transcribe(
#             file_path,
#             beam_size=self.beam_size,
#             **kwargs
#         )
#         return "".join([seg.text for seg in segments])

#     def transcribe_bytes(
#         self,
#         audio_bytes: bytes,
#         sampling_rate: int = 16000,
#         **kwargs
#     ) -> str:
#         audio = (
#             np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#         )
#         segments, _ = self.model.transcribe(
#             audio,
#             beam_size=self.beam_size,
#             **kwargs
#         )
#         return "".join([seg.text for seg in segments])

#     async def transcribe_stream(
#         self,
#         chunk_duration: float = 3.0,
#         sampling_rate: int = 16000,
#         **kwargs
#     ):
#         import asyncio

#         loop = asyncio.get_event_loop()
#         stream = sd.InputStream(
#             samplerate=sampling_rate,
#             channels=1,
#             dtype="int16"
#         )
#         stream.start()
#         try:
#             while True:
#                 data, _ = await loop.run_in_executor(
#                     None,
#                     stream.read,
#                     int(chunk_duration * sampling_rate)
#                 )
#                 audio_bytes = data.flatten().tobytes()
#                 yield self.transcribe_bytes(
#                     audio_bytes,
#                     sampling_rate=sampling_rate,
#                     **kwargs
#                 )
#         finally:
#             stream.stop()
#             stream.close()

#     def record_and_transcribe(
#         self,
#         duration: float = 5.0,
#         chunk_size: float = 20.0,
#         sampling_rate: int = 16000,
#         print_live: bool = True,
#         **kwargs
#     ) -> str:
#         """
#         Records audio from the microphone and returns transcription.
#         Automatically splits long recordings into chunks for better performance.

#         Args:
#             duration: Total recording duration in seconds.
#             chunk_size: How long each chunk should be (in seconds).
#             sampling_rate: Sample rate for recording.
#             print_live: If True, prints each chunk's transcription as it's processed.
#             **kwargs: Additional parameters for transcription.

#         Returns:
#             Full transcription.
#         """
#         print(f"Recording for {duration} seconds...")
#         recording = sd.rec(
#             int(duration * sampling_rate),
#             samplerate=sampling_rate,
#             channels=1,
#             dtype='int16'
#         )
#         sd.wait()
#         print("Recording complete. Transcribing in chunks...")

#         total_samples = int(duration * sampling_rate)
#         chunk_samples = int(chunk_size * sampling_rate)
#         full_text = ""

#         for i in range(0, total_samples, chunk_samples):
#             chunk = recording[i:i + chunk_samples]
#             audio_bytes = chunk.flatten().tobytes()
#             text = self.transcribe_bytes(audio_bytes, sampling_rate=sampling_rate, **kwargs)
#             if print_live:
#                 print(f"[Chunk {i // chunk_samples + 1}] {text}")
#             full_text += text + " "

#         return full_text.strip()

# stt = STTModule(model_size="small", device="cpu", compute_type="int8")
# text = stt.record_and_transcribe(duration=60, chunk_size=5)
# print("You said:", text)  

# # stt_module 2.py

# """
# Speech-to-Text (STT) module using Faster Whisper (CTranslate2)
# Requires: Python 3.12+, faster-whisper, sounddevice, numpy
# """

# import numpy as np
# from faster_whisper import WhisperModel
# import sounddevice as sd
# import soundfile as sf

# class STTModule:
#     """
#     STTModule wraps the Faster Whisper model for file-based and streaming transcription.

#     Example:
#         stt = STTModule(
#             model_size="small",
#             device="cpu",
#             compute_type="int8",
#             beam_size=5
#         )
#         text = stt.record_and_transcribe(duration=5)
#         print(text)
#     """

#     def __init__(
#         self,
#         model_size: str = "small",
#         device: str = "cpu",
#         compute_type: str = "int8",
#         beam_size: int = 5
#     ):
#         self.model = WhisperModel(
#             model_size,
#             device=device,
#             compute_type=compute_type
#         )
#         self.beam_size = beam_size

#     def transcribe_file(self, file_path: str, **kwargs) -> str:
#         segments, _ = self.model.transcribe(
#             file_path,
#             beam_size=self.beam_size,
#             **kwargs
#         )
#         return "".join([seg.text for seg in segments])

#     def transcribe_bytes(
#         self,
#         audio_bytes: bytes,
#         sampling_rate: int = 16000,
#         **kwargs
#     ) -> str:
#         audio = (
#             np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
#         )
#         segments, _ = self.model.transcribe(
#             audio,
#             beam_size=self.beam_size,
#             **kwargs
#         )
#         return "".join([seg.text for seg in segments])

#     async def transcribe_stream(
#         self,
#         chunk_duration: float = 3.0,
#         sampling_rate: int = 16000,
#         **kwargs
#     ):
#         import asyncio

#         loop = asyncio.get_event_loop()
#         stream = sd.InputStream(
#             samplerate=sampling_rate,
#             channels=1,
#             dtype="int16"
#         )
#         stream.start()
#         try:
#             while True:
#                 data, _ = await loop.run_in_executor(
#                     None,
#                     stream.read,
#                     int(chunk_duration * sampling_rate)
#                 )
#                 audio_bytes = data.flatten().tobytes()
#                 yield self.transcribe_bytes(
#                     audio_bytes,
#                     sampling_rate=sampling_rate,
#                     **kwargs
#                 )
#         finally:
#             stream.stop()
#             stream.close()

#     def record_and_transcribe(
#         self,
#         duration: float = 5.0,
#         sampling_rate: int = 16000,
#         **kwargs
#     ) -> str:
#         """
#         Records audio from the microphone and returns transcription.

#         Args:
#             duration: Duration of recording in seconds.
#             sampling_rate: Sample rate for recording.
#             **kwargs: Additional parameters for transcription.

#         Returns:
#             Transcribed text.
#         """
#         print(f"Recording for {duration} seconds...")
#         recording = sd.rec(
#             int(duration * sampling_rate),
#             samplerate=sampling_rate,
#             channels=1,
#             dtype='int16'
#         )
#         sd.wait()
#         print("Recording complete. Transcribing...")
#         audio_bytes = recording.flatten().tobytes()
#         return self.transcribe_bytes(audio_bytes, sampling_rate=sampling_rate, **kwargs)


# stt = STTModule(model_size="small", device="cpu", compute_type="int8")
# text = stt.record_and_transcribe(duration=5)
# print("You said:", text)

