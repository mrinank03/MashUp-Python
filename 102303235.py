#!/usr/bin/env python3
"""
YouTube Mashup CLI Tool
Roll Number: 102303235

Usage:
    python 102303235.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>

Example:
    python 102303235.py "Sharry Maan" 20 20 102303235-output.mp3
"""

import sys
import os
import time
import random
import shutil
import logging
from typing import List, Dict, Any, Optional
from pydub import AudioSegment
import yt_dlp

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
# Suppress yt-dlp deprecation warnings
logging.getLogger('yt_dlp').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

TEMP_DIR = "temp_audio"

# User agents for requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]


# Helper functions

def validate_args(args):
    """Validate and parse command-line arguments."""
    if len(args) != 5:
        print(
            "Error: Exactly 4 arguments required.\n"
            "Usage: python 102303235.py <SingerName> <NumberOfVideos> "
            "<AudioDuration> <OutputFileName>"
        )
        sys.exit(1)

    singer_name = args[1]
    try:
        num_videos = int(args[2])
    except ValueError:
        print("Error: NumberOfVideos must be a positive integer.")
        sys.exit(1)

    try:
        audio_duration = int(args[3])
    except ValueError:
        print("Error: AudioDuration must be a positive integer.")
        sys.exit(1)

    output_file = args[4]

    if num_videos <= 0:
        print("Error: NumberOfVideos must be a positive integer.")
        sys.exit(1)
    if audio_duration <= 0:
        print("Error: AudioDuration must be a positive integer.")
        sys.exit(1)
    if not output_file.endswith(".mp3"):
        print("Error: OutputFileName must end with .mp3")
        sys.exit(1)

    return singer_name, num_videos, audio_duration, output_file


def search_videos(singer_name, num_videos):
    """Search YouTube for singer's videos and return URLs."""
    logger.info("Searching YouTube for '%s' videos…", singer_name)
    query = f"{singer_name} songs"
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
    search_query = f"ytsearch{num_videos}:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
            result = ydl.extract_info(search_query, download=False)
    except Exception as exc:
        logger.error("Failed to search YouTube: %s", exc)
        sys.exit(1)

    urls = []
    if result and "entries" in result and result["entries"]:
        for entry in result["entries"]:  # type: ignore
            if entry and entry.get("url"):
                urls.append(entry["url"])
            elif entry and entry.get("id"):
                urls.append(f"https://www.youtube.com/watch?v={entry['id']}")

    if not urls:
        print(f"Error: No videos found for singer '{singer_name}'.")
        sys.exit(1)

    logger.info("Found %d video URL(s).", len(urls))
    return urls


def download_audio(url, index):
    """Download audio from YouTube URL."""
    output_template = os.path.join(TEMP_DIR, f"audio_{index}.%(ext)s")
    
    # Optimized format options for better success
    format_options = [
        "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
        "bestaudio[filesize<50M]/bestaudio",
        "worst[ext=m4a]/worst[ext=mp4]/worst",
        "18",  # Common YouTube format
    ]
    
    for format_sel in format_options:
        ydl_opts: Dict[str, Any] = {
            "format": format_sel,
            "outtmpl": output_template,
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
            # Add random delay
            time.sleep(random.uniform(1, 3))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                ydl.download([url])
            
            # Check if download succeeded
            expected_path = os.path.join(TEMP_DIR, f"audio_{index}.mp3")
            if os.path.exists(expected_path):
                return expected_path

            # Check for any variant of the downloaded file
            for fname in os.listdir(TEMP_DIR):
                if fname.startswith(f"audio_{index}.") and not fname.endswith(".part"):
                    return os.path.join(TEMP_DIR, fname)
                    
        except Exception as exc:
            logger.debug(f"Format '{format_sel}' failed: {exc}")
            continue
    
    # All formats failed
    logger.warning("Could not download %s with any format", url)
    return None


def cut_and_merge(audio_paths, duration_sec, output_file):
    """Create mashup by combining audio clips."""
    duration_ms = duration_sec * 1000
    combined = AudioSegment.empty()

    for path in audio_paths:
        try:
            audio = AudioSegment.from_file(path)
            clip = audio[:duration_ms]
            combined += clip
            logger.info("Added %d ms from %s", len(clip), os.path.basename(path))
        except Exception as exc:
            logger.warning("Skipping %s: %s", path, exc)

    if len(combined) == 0:
        print("Error: No audio clips could be processed.")
        sys.exit(1)

    combined.export(output_file, format="mp3")
    logger.info("Mashup saved to %s (%d ms total)", output_file, len(combined))


def cleanup():
    """Clean up temporary files."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        logger.info("Cleaned up temporary files.")


# Main", "oldString": "# ===================================================================\n# Main\n# ===================================================================

def main():
    singer_name, num_videos, audio_duration, output_file = validate_args(sys.argv)

    # Prepare temp directory
    os.makedirs(TEMP_DIR, exist_ok=True)

    try:
        # Step 1 – Search
        urls = search_videos(singer_name, num_videos)

        # Step 2 – Download
        logger.info("Downloading %d audio tracks…", len(urls))
        audio_paths = []
        
        for i, url in enumerate(urls, start=1):
            logger.info("Downloading %d/%d … (got %d so far)", i, len(urls), len(audio_paths))
            path = download_audio(url, i)
            if path:
                audio_paths.append(path)
                logger.info("✅ Success! Downloaded: %s", os.path.basename(path))
                
                # Early exit if we have enough
                if len(audio_paths) >= 5:
                    logger.info("Got %d downloads, that's sufficient!", len(audio_paths))
                    break
            else:
                logger.warning("❌ Failed to download video %d", i)
            
            # Stop early if we tried many and got some success
            if i >= 10 and len(audio_paths) >= 3:
                logger.info("Tried %d, got %d successes. Stopping.", i, len(audio_paths))
                break

        if not audio_paths:
            print("\n❌ Failed to download any audio.")
            print("This usually happens when YouTube blocks downloads.")
            print("\n💡 Try:")
            print("  • Different singer (try 'Kishore Kumar' or 'Lata Mangeshkar')")
            print("  • Fewer videos (5-8 instead of 10+)")
            print("  • Wait 10-15 minutes and try again")
            sys.exit(1)

        logger.info("Successfully downloaded %d/%d audio files.", len(audio_paths), len(urls))

        # Step 3 – Cut & merge
        cut_and_merge(audio_paths, audio_duration, output_file)

        print(f"\n✅ Mashup created successfully: {output_file}")

    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        sys.exit(1)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
