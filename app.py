from flask import Flask, render_template, request, send_from_directory, session, Response
import yt_dlp
import requests
import os
import json
import tempfile


app = Flask(__name__)
app.secret_key = 'secret-key'


@app.route('/')
def index():
    return render_template('index.html', title=None)

@app.route('/', methods=['POST', 'GET'])
def download():
    url = request.form['url']

    try:
        

        # Konfigurasi yt-dlp
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Gabungkan video dan audio terbaik
            'noplaylist': True,
            'outtmpl': '-',  # Output streaming
            'cookies': cookies_path,
            
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # Unduh video
            
            formats = info.get('formats', [])
            if not formats:
                raise ValueError("Format video tidak tersedia")

            # Cari format terbaik dengan audio dan video
            video_url = None
            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    video_url = fmt.get('url')
                    break

            if not video_url:
                raise ValueError("Tidak ada format video dengan audio tersedia")

            # Ambil detail tambahan
            video_title = info.get('title', 'Video')
            thumbnail_url = info.get('thumbnail')

        # Simpan URL video untuk diakses pengguna
        session['video_url'] = video_url

        return render_template('index.html', title=video_title, gambar=thumbnail_url)
    except Exception as e:
        error_message = f"URL tidak ditemukan atau terjadi masalah lainnya: "
        return render_template('index.html', title=None, filename=None, gambar=None, error=error_message)


@app.route('/download_file', methods=['POST', 'GET'])
def download_file():
    video_url = session.get('video_url')
    if not video_url:
        return "URL video tidak ditemukan", 404

    # Unduh video langsung dari URL
    return Response(
        requests.get(video_url, stream=True).content,
        content_type='video/mp4',
        headers={'Content-Disposition': f'attachment; filename="video.mp4"'}
    )



@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(port=8000)
