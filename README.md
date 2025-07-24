# SIM-TALK: a Real-Time S2ST (Speech-to-Speech Translation)

## Introduction

This repository offers two Python scripts that leverage Meta’s **SeamlessM4T** model to perform continuous, real-time speech-to-speech translation. Simply speak into your microphone, and the system will detect your language (Russian or English), translate your words into the opposite language, and play back the translation without interruption.

The goal is to empower developers and researchers to build tools that break down language barriers—whether for business, security, social interaction, or accessibility.

## How It Works

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/streaming-translation.git
   cd streaming-translation
   ```

2. **Create a virtual environment & install dependencies**

   ```bash
   conda create --name s2st_real_time python=3.12
   conda activate s2st_real_time
   pip install -r requirements.txt
   ```

3. **Choose your mode**

   * **Real-Time**: continuous microphone input → live translation

     ```bash
     python real_time.py
     ```
   * **Offline**: translate a single prerecorded audio file

     ```bash
     python offline_one_hit.py --input path/to/audio.wav
     ```

4. **Speak freely**

   * The script auto-detects **Russian ↔ English**.
   * To customize languages, edit in `real_time.py` or `offline_one_hit.py`:

     ```python
     src_lang = detect_language(audio_chunk, fs)
     tgt_lang = 'eng' if src_lang == 'rus' else 'rus'
     ```

## Configuration

* **Chunk duration**: adjust `CHUNK_DURATION` (default: 5 s) in `real_time.py` to trade off latency vs. translation quality.
* **Models**: change the processor/model paths to use different sizes (e.g., `seamless-m4t-small`).

## License

This project is released under the **PolyForm Noncommercial License 1.0.0**, which **strictly prohibits** any commercial, academic, or research use without prior written permission from the author.

**License Summary:**

* 🚫 No commercial use
* 🚫 No academic or research use
* ✅ Use allowed only with explicit consent

To request permission, please open an issue or contact the project owner:

* Email: [guzzettagianluca@gmail.com](mailto:guzzettagianluca@gmail.com)
* Website: [https://www.gianlucaguzzetta.com](https://www.gianlucaguzzetta.com)

## Collaborations

If you want to collaborate and improve the code, open a PR or send an email to [guzzettagianluca@gmail.com](mailto:guzzettagianluca@gmail.com).