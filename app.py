from flask import Flask, render_template, request, send_file, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html', title=None )

@app.route('/', methods=['POST'])
def download():
    url = request.form['url']

    try:
        # Konfigurasi yt-dlp
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Simpan di folder downloads
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)  # Unduh video
            video_title = info.get('title', 'video')
            video_filename = ydl.prepare_filename(info)
            thumbnail_url = info.get('thumbnail')

        return render_template('index.html', title=video_title, filename=video_filename, gambar=thumbnail_url)  
    except Exception as e:
        error_message = "URL tidak ditemukan atau terjadi masalah lainnya."
        return render_template('index.html', title=None, filename=None, gambar=None, error=error_message)

@app.route('/download_file/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
