import soundfile as sf
from datetime import datetime
from utils import load_model, record_audio_interactive, translate_speech, play_audio

def main():
    # Load the translation processor and model (ASR not needed here)
    processor, model = load_model(with_asr=False)

    running = True
    while running:
        # Prompt the user to choose translation direction
        print("Choose direction:")
        print("  1) English → Russian")
        print("  2) Russian  → English")
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            src, tgt = "eng", "rus"
        elif choice == "2":
            src, tgt = "rus", "eng"
        else:
            print("Invalid choice. Exiting.")
            return

        fs = 16000  # Sampling rate (Hz)

        # Record audio from the microphone until Enter is pressed
        audio_in = record_audio_interactive(fs=fs)

        # Save the raw input with a timestamped filename
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_fname = f"input_{src}_{tgt}_{ts}.wav"
        sf.write(input_fname, audio_in, fs)
        print(f"✅ Saved input → {input_fname}")

        # Perform translation: src_lang → tgt_lang
        audio_out = translate_speech(
            processor, model, audio_in, fs=fs, src_lang=src, tgt_lang=tgt
        )

        # Play back the translated audio and save to disk
        play_audio(audio_out, fs)
        out_fname = f"translated_{src}_{tgt}_{ts}.wav"
        sf.write(out_fname, audio_out, fs)
        print(f"✅ Saved translation → {out_fname}")

        # Ask if the user wants to exit or continue
        exit_choice = input("Type 'exit' to quit or press Enter to continue: ").strip()
        if exit_choice.lower() == "exit":
            running = False

if __name__ == "__main__":
    main()
