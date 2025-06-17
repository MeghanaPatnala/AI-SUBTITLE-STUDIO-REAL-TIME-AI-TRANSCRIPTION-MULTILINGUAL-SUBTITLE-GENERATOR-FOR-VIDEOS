

# 🎬 AI-SUBTITLE-STUDIO
> A real-time AI-powered transcription and multilingual subtitle generation app for videos (YouTube or local).

🧠 Built with Faster-Whisper + Google Translate + Flask  
🌐 Supports multiple languages: English, Telugu, Hindi, Tamil, Malayalam, Korean  
🎯 Extracts audio → Transcribes speech → Translates → Generates SRT + downloadable transcript

---

## 📌 Features

✅ Upload videos or paste YouTube links  
✅ Extracts audio and performs speech-to-text using Whisper  
✅ Translates transcript into selected language using Google Translate  
✅ Generates subtitle (SRT) and transcript files  
✅ Clean and simple web interface  
✅ Supports YouTube Shorts  
✅ Download subtitles and transcript files  

---

## 🛠️ Tech Stack

| Layer        | Technology                     |
|--------------|--------------------------------|
| Backend      | Python, Flask, Faster-Whisper  |
| Translation  | deep-translator (Google API)   |
| Audio/Video  | moviepy, yt-dlp                 |
| Frontend     | HTML5, CSS3 (custom)           |

---

## 📸 Screenshots

Upload screen:  
![Upload screen]("")

Result page:  
![Result screen](screenshots/result.png)

---

## 🚀 How It Works

1. 🎥 Upload a video or paste a YouTube URL  
2. 🧠 Extracts audio and uses Faster-Whisper for transcription  
3. 🌍 Translates dialogue into your chosen language  
4. 📝 Outputs:
    - Translated transcript (.txt)
    - Subtitle file (.srt)
    - In-browser video + text display  
5. ⬇️ Download your transcript or subtitles!

---

