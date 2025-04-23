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


