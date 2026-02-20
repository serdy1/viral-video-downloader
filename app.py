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
        }

        # Check if ffmpeg is in path, else specific paths could be added
        # For now, let yt-dlp try to find it automatically.

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
        elif format_choice == 'best':
            ydl_opts['format'] = 'best'
        else:
            # Assume it's a format_id from the analyze step
            ydl_opts['format'] = format_choice + '+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Return the filename for download
        return jsonify({'filename': os.path.basename(filename)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'socket_timeout': 10,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Filter and prepare formats
            formats = []
            for f in info.get('formats', []):
                # Include combined formats or video-only formats that can be merged
                if f.get('vcodec') != 'none':
                    formats.append({
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution') or f.get('format_note'),
                        'filesize': f.get('filesize') or f.get('filesize_approx'),
                        'format_id': f.get('format_id'),
                        'note': f.get('format_note') or f.get('ext')
                    })
            
            # If still no formats, just take the first few
            if not formats:
                for f in info.get('formats', [])[:5]:
                    formats.append({
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution') or 'N/A',
                        'filesize': f.get('filesize'),
                        'format_id': f.get('format_id'),
                        'note': f.get('format_note') or 'Best'
                    })

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'view_count': info.get('view_count'),
                'uploader': info.get('uploader'),
                'formats': formats
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)