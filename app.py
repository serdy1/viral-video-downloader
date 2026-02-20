from flask import Flask, request, render_template, send_from_directory, jsonify
import yt_dlp
import os

app = Flask(__name__, template_folder='.', static_folder='static')

DOWNLOAD_DIR = 'downloads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_choice = request.form.get('format', 'best')  # Default to best

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'ffmpeg_location': '/usr/bin/ffmpeg',
        }

        if format_choice == 'mp4':
            ydl_opts['format'] = 'best[ext=mp4]'
        elif format_choice == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif format_choice == 'webm':
            ydl_opts['format'] = 'best[ext=webm]'
        else:
            ydl_opts['format'] = 'best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Return the filename for download
        return jsonify({'filename': os.path.basename(filename)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)