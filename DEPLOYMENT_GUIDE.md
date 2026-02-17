# YouTube Mashup - Deployment & Fixes Guide

## 🔧 Fixes Applied (Feb 17, 2026)

### Problem: HTTP 403 Forbidden Errors
YouTube was blocking download requests with 403 errors due to:
- Outdated user agents
- Missing browser headers
- No YouTube-specific extractor arguments
- Insufficient retry logic

### Solutions Implemented

#### 1. **Enhanced yt-dlp Configuration**
- ✅ Updated to use `player_client: ["android", "web"]` extractor argument
- ✅ Added `player_skip: ["webpage", "configs"]` to bypass web player parsing
- ✅ Increased timeouts: 30s socket timeout (was 15-20s)
- ✅ More retries: 3 extractor retries, 3 fragment retries

#### 2. **Better HTTP Headers**
```python
"http_headers": {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-us,en;q=0.5",
    "Sec-Fetch-Mode": "navigate",
}
```

#### 3. **Improved Format Selection**
Now tries these formats in order:
1. `bestaudio[ext=m4a]` - Best m4a audio
2. `bestaudio[ext=webm]` - Best webm audio
3. `bestaudio` - Best available audio
4. `best[height<=360]` - Lower resolution video (easier to download)
5. `worst` - Fallback to worst quality

#### 4. **Enhanced Retry Logic**
- Increased sleep intervals (2-5 seconds between downloads)
- Added 2-second wait between format attempts
- Better error logging with success indicators (✅)

#### 5. **Updated Dependencies**
```
streamlit>=1.29.0
yt-dlp>=2024.12.6  # Latest version with YouTube fixes
pydub>=0.25.1
python-dotenv>=1.0.0
audioop-lts>=0.2.1
```

## 🚀 Deployment Instructions

### For Streamlit Cloud

1. **Push Changes to GitHub**
   ```bash
   git add .
   git commit -m "Fix: Enhanced yt-dlp config to resolve HTTP 403 errors"
   git push origin main
   ```

2. **Update Streamlit Cloud App**
   - Go to https://share.streamlit.io/
   - Find your app in the dashboard
   - Click "Reboot app" or wait for auto-deploy
   - The new `requirements.txt` will trigger package updates

3. **Verify Secrets (Already Configured)**
   Your secrets are correctly set:
   ```toml
   EMAIL_ADDRESS="mrinank.2003@gmail.com"
   EMAIL_PASSWORD="eojz ypty odmh mprq"
   FALLBACK_MODE=true
   ```

4. **Monitor Logs**
   - Watch for "✅ Successfully downloaded" messages
   - Should see fewer 403 errors
   - Fallback mode will activate if downloads still fail

### For Local Testing

1. **Update Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Set Environment Variables**
   Create `.env` file:
   ```env
   EMAIL_ADDRESS=mrinank.2003@gmail.com
   EMAIL_PASSWORD=eojz ypty odmh mprq
   FALLBACK_MODE=true
   ```

3. **Test the App**
   ```bash
   streamlit run app.py
   ```

4. **Test CLI Tool**
   ```bash
   python 102303235.py "Arijit Singh" 8 20 test-output.mp3
   ```

## ⚠️ Important Notes

### YouTube Download Limitations
Even with these fixes, YouTube may still block downloads in certain scenarios:
- **High volume requests**: Too many downloads in short time
- **IP-based blocking**: Some IPs are flagged by YouTube
- **Regional restrictions**: Some videos blocked in certain regions
- **Account-based blocking**: YouTube may require sign-in

### Fallback Mode
With `FALLBACK_MODE=true`, the app will:
1. Try to download real YouTube videos first
2. If downloads fail, create a working demo mashup
3. Still send email and allow download
4. Show clear warnings to user

This ensures the app **always works** even when YouTube blocks downloads.

### Best Practices
- **Test with popular artists**: "Arijit Singh", "Kishore Kumar", "Lata Mangeshkar"
- **Use moderate video counts**: 5-10 videos works better than 20
- **Allow longer durations**: 20-30 seconds is optimal
- **Wait between tests**: Don't hammer YouTube with requests

## 🔍 Troubleshooting

### If Still Getting 403 Errors:

1. **Update yt-dlp to latest**
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **Try different artists**
   Some artists' videos are more restricted than others

3. **Reduce video count**
   Try 5 videos instead of 10+

4. **Check Streamlit Cloud logs**
   Look for specific error messages

5. **Verify FFmpeg is installed**
   Check packages.txt has `ffmpeg`

### If Email Fails:

1. **Verify Gmail App Password**
   - Not regular password - needs App Password
   - Generate at: https://myaccount.google.com/apppasswords

2. **Check 2FA is enabled**
   App Passwords require 2-factor authentication

3. **Verify email in secrets**
   Must match exactly (no extra spaces)

## 📊 Expected Behavior

### Successful Run:
```
🔍 Searching YouTube…
Found 8 videos
⬇️ Downloading audio…
⬇️ Downloading track 1/8... (0 successful)
✅ Successfully downloaded with format: bestaudio[ext=m4a]
⬇️ Downloading track 2/8... (1 successful)
✅ Successfully downloaded with format: bestaudio[ext=m4a]
...
✂️ Cutting & merging clips…
Creating ZIP…
📧 Sending email…
✅ Mashup sent to your@email.com! Check your inbox.
```

### With Fallback:
```
🔍 Searching YouTube…
Found 8 videos
⬇️ Downloading audio…
⚠️ Downloads failed, creating working demo instead
Creating demo mashup...
Creating ZIP…
📧 Sending email…
✅ Mashup sent to your@email.com! Check your inbox.
```

## 🎯 Next Steps

1. **Deploy to Streamlit Cloud** (reboot app)
2. **Test with real user flow**
3. **Monitor logs for success rate**
4. **Adjust FALLBACK_MODE** based on success rate

## 📝 Technical Details

### Key Changes in Code:

**app.py** and **102303235.py**:
- Line ~105: Updated `search_youtube()` with better headers
- Line ~145: Enhanced `download_audio()` with extractor_args
- Line ~160: Added YouTube-specific player_client configuration
- Line ~180: Improved error handling with detailed logs

### Why These Fixes Work:

1. **Android player client**: YouTube's Android API is more permissive
2. **Skip webpage parsing**: Avoids complex JavaScript parsing that often fails
3. **Better headers**: Makes requests look more like real browser
4. **More retries**: Handles temporary failures gracefully
5. **Latest yt-dlp**: Includes latest YouTube workarounds

---

**Updated**: February 17, 2026
**Status**: Ready for deployment ✅
