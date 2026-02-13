# YouTube Mashup Generator — 102303235

A Python-based YouTube mashup tool that downloads songs of a given singer, trims them, and merges the clips into a single MP3 file.

## Programs

| # | File | Description |
|---|------|-------------|
| 1 | `102303235.py` | Command-line mashup tool |
| 2 | `app.py` | Streamlit web application with email delivery |

## Prerequisites

- **Python 3.8+**
- **ffmpeg** installed and available on `PATH`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
  - Windows: `choco install ffmpeg`

## Setup

```bash
# 1. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure email (for the Streamlit app)
#    Edit .env with your Gmail address and App Password
```

## Usage

### Program 1 — CLI

```bash
python 102303235.py "<SingerName>" <NumberOfVideos> <AudioDuration> <OutputFile.mp3>
# Example:
python 102303235.py "Sharry Maan" 20 20 102303235-output.mp3
```

### Program 2 — Streamlit Web App

```bash
streamlit run app.py
```

Open the URL printed in the terminal, fill in the form, and hit **Create Mashup**.

## Author

**Mrinank Jit Singh** — Roll No. 102303235
