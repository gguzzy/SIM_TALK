import sounddevice as sd
import queue
import threading
from utils import load_model, translate_worker, stream_callback

def main():
    # Load processor, translation model, and ASR pipeline for auto-detection
    processor, model, asr = load_model(with_asr=True)

    fs = 16000                  # Sampling rate (Hz)
    CHUNK_DURATION = 5          # Chunk length in seconds
    CHUNK_SIZE = fs * CHUNK_DURATION

    audio_queue = queue.Queue() # Queue for audio chunks
    buffer = []                 # Buffer to accumulate incoming audio

    # Start the background thread that handles translation & playback
    translator_thread = threading.Thread(
        target=translate_worker,
        args=(processor, model, asr, audio_queue, fs),
        daemon=True
    )
    translator_thread.start()

    try:
        # Open the microphone stream and process incoming data
        with sd.InputStream(
            samplerate=fs,
            channels=1,
            callback=lambda indata, frames, time, status: stream_callback(
                indata, frames, time, status, buffer, CHUNK_SIZE, audio_queue
            )
        ):
            print(
                f"🎙 Streaming Russian ↔ English in real time "
                f"(processing {CHUNK_DURATION}s chunks). Ctrl+C to stop."
            )
            while True:
                sd.sleep(1000)

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")

    finally:
        # Signal the worker to exit and wait for it to finish
        audio_queue.put(None)
        translator_thread.join()

if __name__ == "__main__":
    main()
