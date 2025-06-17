import os
import uuid
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
import yt_dlp

app = Flask(__name__)

# Folders
UPLOAD_FOLDER = "uploads"
TRANSCRIPT_FOLDER = "transcripts"
SRT_FOLDER = "subtitles"
VTT_FOLDER = "vtt"                          # <— New folder for WebVTT
for d in (UPLOAD_FOLDER, TRANSCRIPT_FOLDER, SRT_FOLDER, VTT_FOLDER):
    os.makedirs(d, exist_ok=True)

# Load Whisper model once
model = WhisperModel("base")

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        target_lang = request.form.get("target_lang")
        video_url   = request.form.get("video_url")
        video_file  = request.files.get("video_file")

        # 1️⃣ Save or download video
        if video_file and video_file.filename:
            fn = secure_filename(video_file.filename)
            video_path = os.path.join(UPLOAD_FOLDER, fn)
            video_file.save(video_path)

        elif video_url:
            try:
                if "youtube.com/shorts" in video_url:
                    video_url = video_url.replace("shorts/", "watch?v=")
                opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(UPLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                    'quiet': True
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    video_path = ydl.prepare_filename(info)
            except Exception as e:
                error = f"⚠️ Could not download video: {e}"
                return render_template("index.html", error=error)
        else:
            error = "⚠️ Upload a file or enter a YouTube URL."
            return render_template("index.html", error=error)

        # 2️⃣ Extract audio
        clip = VideoFileClip(video_path)
        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        clip.audio.write_audiofile(audio_path)

        # 3️⃣ Transcribe & translate line‐by‐line
        raw, _ = model.transcribe(audio_path)
        segments = []
        for s in raw:
            text = s.text.strip()
            try:
                trans = GoogleTranslator(source="auto", target=target_lang).translate(text)
            except:
                trans = text
            segments.append({
                "start": s.start,
                "end":   s.end,
                "translated": trans
            })

        # 4️⃣ Save transcript (txt)
        tid = f"{uuid.uuid4().hex}.txt"
        with open(os.path.join(TRANSCRIPT_FOLDER, tid), "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(seg["translated"] + "\n")

        # 5️⃣ Save SRT and also generate WebVTT
        sid = f"{uuid.uuid4().hex}.srt"
        vid = f"{uuid.uuid4().hex}.vtt"

        # Write SRT
        with open(os.path.join(SRT_FOLDER, sid), "w", encoding="utf-8") as f_srt:
            for i, seg in enumerate(segments, 1):
                start = format_ts(seg["start"])
                end   = format_ts(seg["end"])
                f_srt.write(f"{i}\n{start} --> {end}\n{seg['translated']}\n\n")

        # Write WebVTT
        with open(os.path.join(VTT_FOLDER, vid), "w", encoding="utf-8") as f_vtt:
            f_vtt.write("WEBVTT\n\n")
            for seg in segments:
                start = format_ts_webvtt(seg["start"])
                end   = format_ts_webvtt(seg["end"])
                f_vtt.write(f"{start} --> {end}\n{seg['translated']}\n\n")

        return render_template(
            "result.html",
            video_filename=os.path.basename(video_path),
            segments=segments,
            transcript_file=tid,
            srt_file=sid,
            vtt_file=vid    # Pass the new VTT name to template
        )

    return render_template("index.html", error=error)


def format_ts(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def format_ts_webvtt(sec):
    # WebVTT uses a decimal hour:minute:second.millisecond format
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"


@app.route("/uploads/<fn>")
def uploaded_file(fn):
    return send_from_directory(UPLOAD_FOLDER, fn)

@app.route("/transcripts/<fn>")
def download_transcript(fn):
    return send_from_directory(TRANSCRIPT_FOLDER, fn, as_attachment=True)

@app.route("/subtitles/<fn>")
def download_srt(fn):
    return send_from_directory(SRT_FOLDER, fn, as_attachment=True)

@app.route("/vtt/<fn>")
def download_vtt(fn):
    return send_from_directory(VTT_FOLDER, fn, as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True)
