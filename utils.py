import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model, pipeline
import numpy as np
import sounddevice as sd
import sys
from langdetect import detect

def load_model(with_asr: bool = False):
    """
    Carica il processor e il modello SeamlessM4T.
    Se with_asr=True, restituisce anche una pipeline ASR Whisper-small per il rilevamento della lingua.
    """
    # ---- 1. Load processor & model ----
    processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
    model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large")

    if with_asr:
        # ---- 2. Load ASR pipeline ----
        asr = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-small",
            chunk_length_s=5,
            device=0 if torch.cuda.is_available() else -1
        )
        return processor, model, asr

    return processor, model

def record_audio_interactive(fs: int = 16000) -> np.ndarray:
    """Record audio from your mic, start/stop via Enter key."""
    frames = []

    def callback(indata, _frames, _time, status):
        if status:
            print(f"⚠️  {status}")
        frames.append(indata.copy())

    print("Press Enter to start recording.")
    input()
    print("🎙  Recording... press Enter again to stop.")
    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        input()
    print("🛑  Recording stopped.")

    audio = np.concatenate(frames, axis=0).squeeze()
    return audio

def translate_speech(processor, model, audio: np.ndarray, fs: int, src_lang: str, tgt_lang: str) -> np.ndarray:
    """Run SeamlessM4Tv2Model to translate raw audio from src_lang → tgt_lang."""
    inputs = processor(audios=audio, sampling_rate=fs, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, tgt_lang=tgt_lang)
    return outputs[0].cpu().numpy().squeeze()

def play_audio(audio: np.ndarray, fs: int):
    """Play a NumPy audio array at sample rate fs."""
    sd.play(audio, fs)
    sd.wait()


def detect_language(asr, audio: np.ndarray, fs: int) -> str:
    """Detects whether audio is in English or Russian."""
    # Run ASR to get text
    result = asr(audio)
    text = result.get("text", "")
    # Fallback to langdetect if ASR doesn't provide language
    lang = detect(text) if text else detect(text or " ")
    # Map to our codes
    if lang.startswith("ru"):
        return "rus"
    return "eng"

def translate_worker(processor, model, asr, audio_queue, fs):
    """Worker: auto-detects source language, translates to the other, and plays back."""
    while True:
        audio_chunk = audio_queue.get()
        if audio_chunk is None:
            break
        # detect source and set target
        src_lang = detect_language(asr, audio_chunk, fs)
        tgt_lang = "eng" if src_lang == "rus" else "rus"

        # Prepare inputs and translate
        inputs = processor(audios=audio_chunk, sampling_rate=fs, return_tensors="pt")
        with torch.no_grad():
            generated = model.generate(**inputs, tgt_lang=tgt_lang)
        # Extract waveform and play
        output_audio = generated[0].cpu().numpy().squeeze()
        sd.play(output_audio, fs)
        sd.wait()
    print("Translation worker exiting...")

def stream_callback(indata, frames, time, status, buffer, chunk_size, q):
    if status:
        print(f"⚠️ {status}", file=sys.stderr)
    buffer.append(indata.copy())
    total = np.concatenate(buffer, axis=0).squeeze()
    if total.shape[0] >= chunk_size:
        chunk = total[:chunk_size]
        q.put(chunk)
        remainder = total[chunk_size:]
        buffer.clear()
        if remainder.size > 0:
            buffer.append(remainder.reshape(-1, 1))