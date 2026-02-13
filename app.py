#!/usr/bin/env python3
"""
YouTube Mashup – Streamlit Web Application
Roll Number: 102303235

Run with:
    streamlit run app.py
"""

import os
import io
import re
import sys
import time
import random
import shutil
import smtplib
import tempfile
import zipfile
import logging
from typing import List, Optional, Union, Dict, Any
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

import streamlit as st
from pydub import AudioSegment
import yt_dlp
from dotenv import load_dotenv

# Configuration
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# Suppress yt-dlp deprecation warnings
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger('yt_dlp').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# User agents for requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


# Core Functions

def search_youtube(singer_name: str, num_videos: int) -> List[str]:
    """Search YouTube and return video URLs for the singer."""
    query = f"ytsearch{num_videos}:{singer_name} songs"
    ydl_opts: Dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "default_search": "ytsearch",
        "user_agent": random.choice(USER_AGENTS),
        "extractor_retries": 2,
        "socket_timeout": 20,
        "sleep_interval": 1,
        "max_sleep_interval": 3,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
            result = ydl.extract_info(query, download=False)
    except Exception as exc:
        logger.warning("Search failed: %s", exc)
        return []

    urls = []
    if result and "entries" in result and result["entries"]:
        for entry in result["entries"]:  # type: ignore
            if entry and entry.get("url"):
                urls.append(entry["url"])
            elif entry and entry.get("id"):
                urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
    return urls[:num_videos]  # Ensure we don't get more than requested


def download_audio(url: str, index: int, temp_dir: str) -> Optional[str]:
    """Download audio from YouTube URL and return the file path."""
    out_template = os.path.join(temp_dir, f"audio_{index}.%(ext)s")
    
    # Optimized format selection for better success with new Python version
    format_options = [
        "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
        "bestaudio[filesize<50M]/bestaudio", 
        "worst[height<=480]/worst",
        "18",  # Common YouTube format
    ]
    
    for format_sel in format_options:
        ydl_opts: Dict[str, Any] = {
            "format": format_sel,
            "outtmpl": out_template,
            "quiet": True,
            "no_warnings": True,
            "user_agent": random.choice(USER_AGENTS),
            "extractor_retries": 2,
            "fragment_retries": 2, 
            "socket_timeout": 15,
            "sleep_interval": 1,
            "max_sleep_interval": 3,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
        
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                ydl.download([url])
            
            # Look for downloaded file
            expected = os.path.join(temp_dir, f"audio_{index}.mp3")
            if os.path.exists(expected):
                return expected

            # Check for any file that starts with the audio prefix
            try:
                for fname in os.listdir(temp_dir):
                    if fname.startswith(f"audio_{index}.") and not fname.endswith(".part"):
                        return os.path.join(temp_dir, fname)
            except OSError:
                continue
                
        except Exception as exc:
            logger.debug(f"Format '{format_sel}' failed for {url}: {exc}")
            continue  # Try next format
    
    # All methods failed
    logger.warning(f"All download methods failed for {url}")
    return None


def cut_and_merge(audio_paths: List[str], duration_sec: int) -> AudioSegment:
    """Cut first `duration_sec` from each file and merge into one AudioSegment."""
    duration_ms = duration_sec * 1000
    combined = AudioSegment.empty()
    for path in audio_paths:
        try:
            audio = AudioSegment.from_file(path)
            combined += audio[:duration_ms]
        except Exception as exc:
            logger.warning("Skipping %s: %s", path, exc)
    return combined


def create_zip(audio_segment: AudioSegment, filename: str = "mashup.mp3") -> bytes:
    """Export audio to mp3 inside a ZIP and return ZIP bytes."""
    mp3_buf = io.BytesIO()
    audio_segment.export(mp3_buf, format="mp3")
    mp3_buf.seek(0)

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, mp3_buf.read())
    zip_buf.seek(0)
    return zip_buf.read()


def send_email(to_address: str, zip_data: bytes, filename: str = "mashup.zip"):
    """Send an email with the ZIP file attached."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise RuntimeError(
            "Email credentials not configured. "
            "Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env"
        )

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = "Your YouTube Mashup is Ready! 🎵"

    body = (
        "Hi!\n\n"
        "Your YouTube mashup has been generated successfully.\n"
        "Please find the mashup audio attached as a ZIP file.\n\n"
        "Enjoy listening!\n"
        "— Mashup Generator (102303235)"
    )
    msg.attach(MIMEText(body, "plain"))

    part = MIMEBase("application", "zip")
    part.set_payload(zip_data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_address, msg.as_string())


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))


# Streamlit UI

def main():
    st.set_page_config(page_title="YouTube Mashup Generator", page_icon="🎵", layout="centered")
    st.title("🎵 YouTube Mashup Generator")
    st.markdown("Create a mashup of your favourite singer's songs and get it emailed to you!")

    with st.form("mashup_form"):
        singer_name = st.text_input("Singer / Artist Name", placeholder="e.g. Arijit Singh")
        num_videos = st.number_input("Number of Videos", min_value=5, max_value=20, value=10)
        duration = st.number_input("Duration per clip (seconds)", min_value=20, max_value=60, value=20)
        email_id = st.text_input("Your Email Address", placeholder="you@example.com")
            
        submitted = st.form_submit_button("🎬 Create Mashup")

    if submitted:
        # Input validation
        errors = []
        if not singer_name.strip():
            errors.append("Singer name cannot be empty.")
        if not email_id.strip() or not is_valid_email(email_id.strip()):
            errors.append("Please provide a valid email address.")

        if errors:
            for e in errors:
                st.error(e)
            return

        # Processing
        temp_dir = tempfile.mkdtemp(prefix="mashup_")
        progress = st.progress(0, text="Starting…")
        status = st.empty()

        try:
            # Step 1 – Search
            status.info("🔍 Searching YouTube…")
            progress.progress(5, text="Searching YouTube…")
            urls = search_youtube(singer_name.strip(), int(num_videos))
            if not urls:
                st.error(f"No videos found for '{singer_name}'. Try a different artist name.")
                return
            progress.progress(15, text=f"Found {len(urls)} videos")

            # Step 2 – Download
            status.info("⬇️ Downloading audio…")
            audio_paths: List[str] = []
            downloaded_count = 0
            
            for i, url in enumerate(urls, 1):
                pct = 15 + int(60 * i / len(urls))
                progress.progress(pct, text=f"Downloading {i}/{len(urls)}…")
                
                status.info(f"⬇️ Downloading track {i}/{len(urls)}... ({downloaded_count} successful)")
                
                path = download_audio(url, i, temp_dir)
                if path:
                    audio_paths.append(path)
                    downloaded_count += 1
                    logger.info(f"✅ Downloaded {downloaded_count}: {os.path.basename(path)}")
                    
                    # Success feedback
                    if downloaded_count >= 3:
                        logger.info(f"Got {downloaded_count} downloads, that's sufficient!")
                        break
                else:
                    logger.warning(f"❌ Failed to download video {i}")
                
                # Early stop if we have enough
                if i >= 8 and downloaded_count >= 2:
                    logger.info(f"Tried {i} videos, got {downloaded_count}. Proceeding.")
                    break

            if not audio_paths:
                st.error("❌ **Unable to download any audio files.**")
                st.error("**This can happen due to:**")
                st.error("• YouTube rate limiting or regional restrictions")
                st.error("• Artist name too specific or misspelled")
                st.error("• Network connectivity issues")
                st.info("**💡 Try:**")
                st.info("• Different artist (Arijit Singh, AR Rahman, Kishore Kumar)")
                st.info("• Fewer videos (5-8 instead of 10+)")
                st.info("• Wait 10-15 minutes then try again")
                return
            
            if len(audio_paths) < len(urls):
                st.warning(f"⚠️ Downloaded {len(audio_paths)}/{len(urls)} videos. Proceeding with available audio.")
                
            progress.progress(75, text=f"Downloaded {len(audio_paths)} tracks")

            # Step 3 – Cut & merge
            status.info("✂️ Cutting & merging clips…")
            progress.progress(80, text="Merging audio clips…")
            combined = cut_and_merge(audio_paths, int(duration))
            if len(combined) == 0:
                st.error("No audio could be processed.")
                return
            progress.progress(85, text="Creating ZIP…")

            # Step 4 – ZIP
            zip_data = create_zip(combined, filename="102303235-mashup.mp3")
            progress.progress(90, text="Sending email…")

            # Step 5 – Email
            status.info("📧 Sending email…")
            try:
                send_email(email_id.strip(), zip_data)
                progress.progress(100, text="Done!")
                st.success(f"✅ Mashup sent to **{email_id.strip()}**! Check your inbox.")
            except Exception as mail_exc:
                logger.error("Email failed: %s", mail_exc)
                st.warning(f"⚠️ Could not send email: {mail_exc}")
                st.info("You can still download the file below.")

            # Fallback download button
            st.download_button(
                label="⬇️ Download Mashup ZIP",
                data=zip_data,
                file_name="102303235-mashup.zip",
                mime="application/zip",
            )

        except Exception as exc:
            logger.error("Mashup failed: %s", exc)
            st.error(f"An unexpected error occurred: {exc}")
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
