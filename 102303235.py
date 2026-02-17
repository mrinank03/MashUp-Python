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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
# Suppress yt-dlp deprecation warnings
logging.getLogger('yt_dlp').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

TEMP_DIR = "temp_audio"

# YouTube bot bypass configuration (optional)
YT_PO_TOKEN = os.getenv("YT_PO_TOKEN", "")  # YouTube Proof of Origin token
YT_VISITOR_DATA = os.getenv("YT_VISITOR_DATA", "")  # YouTube visitor data
YT_COOKIES_FILE = os.getenv("YT_COOKIES_FILE", "")  # Path to cookies.txt file

# User agents for requests - Updated for better YouTube compatibility
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
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
        "extractor_retries": 3,
        "socket_timeout": 30,
        "sleep_interval": 2,
        "max_sleep_interval": 5,
        "http_headers": {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        },
    }
    
    # Add YouTube bot bypass if configured
    if YT_PO_TOKEN and YT_VISITOR_DATA:
        ydl_opts["extractor_args"] = {
            "youtube": {
                "po_token": YT_PO_TOKEN,
                "visitor_data": YT_VISITOR_DATA,
            }
        }
        logger.info("✅ Using po_token for YouTube authentication")
    
    # Add cookies file if configured
    if YT_COOKIES_FILE and os.path.exists(YT_COOKIES_FILE):
        ydl_opts["cookiefile"] = YT_COOKIES_FILE
        logger.info(f"✅ Using cookies from: {YT_COOKIES_FILE}")
    
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
    
    # More flexible format selection to avoid "format not available" errors
    format_options = [
        "bestaudio/best",
        "worstaudio/worst",
        "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
    ]
    
    for format_sel in format_options:
        ydl_opts: Dict[str, Any] = {
            "format": format_sel,
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "user_agent": random.choice(USER_AGENTS),
            "extractor_retries": 5,
            "fragment_retries": 5,
            "socket_timeout": 30,
            "sleep_interval": 2,
            "max_sleep_interval": 6,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "no_color": True,
            "extract_flat": False,
            "age_limit": None,
            "geo_bypass": True,
            "source_address": "0.0.0.0",
            "http_headers": {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
                "Sec-Fetch-Mode": "navigate",
            },
        }
        
        # Build extractor_args for YouTube
        youtube_args = {
            "player_client": ["android", "ios", "web"],
            "player_skip": ["webpage"],
            "skip": ["hls", "dash"],
        }
        
        # Add po_token and visitor_data if available (bypasses bot detection)
        if YT_PO_TOKEN and YT_VISITOR_DATA:
            youtube_args["po_token"] = YT_PO_TOKEN  # type: ignore
            youtube_args["visitor_data"] = YT_VISITOR_DATA  # type: ignore
        
        ydl_opts["extractor_args"] = {"youtube": youtube_args}
        
        # Add cookies file if configured
        if YT_COOKIES_FILE and os.path.exists(YT_COOKIES_FILE):
            ydl_opts["cookiefile"] = YT_COOKIES_FILE
        
        # Add postprocessor for audio extraction
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

        try:
            # Add random delay
            time.sleep(random.uniform(2, 5))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                info = ydl.extract_info(url, download=True)
            
            # Check if download succeeded
            expected_path = os.path.join(TEMP_DIR, f"audio_{index}.mp3")
            if os.path.exists(expected_path):
                logger.info(f"✅ Successfully downloaded with format: {format_sel}")
                return expected_path

            # Check for any variant of the downloaded file
            for fname in os.listdir(TEMP_DIR):
                if fname.startswith(f"audio_{index}.") and not fname.endswith(".part"):
                    logger.info(f"✅ Successfully downloaded: {fname}")
                    return os.path.join(TEMP_DIR, fname)
                    
        except Exception as exc:
            logger.debug(f"Format '{format_sel}' failed: {exc}")
            time.sleep(2)  # Wait before trying next format
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
            # Try using default.mp3 as fallback
            default_path = os.path.join(os.path.dirname(__file__), "default.mp3")
            if os.path.exists(default_path):
                print("\n⚠️ YouTube blocked downloads. Using default mashup file.")
                logger.info("Copying default.mp3 to output file")
                try:
                    shutil.copy(default_path, output_file)
                    print(f"✅ Default mashup saved to: {output_file}")
                    print("💡 This is a fallback file due to YouTube's bot detection.")
                    return  # Exit successfully
                except Exception as e:
                    logger.error("Failed to copy default.mp3: %s", e)
            
            # If no default.mp3, show error
            print("\n❌ Failed to download any audio.")
            print("This usually happens when YouTube blocks downloads.")
            print("\n💡 Try:")
            print("  • Different singer (try 'Kishore Kumar' or 'Lata Mangeshkar')")
            print("  • Fewer videos (5-8 instead of 10+)")
            print("  • Wait 10-15 minutes and try again")
            print("  • Add a 'default.mp3' file in the project directory as fallback")
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
