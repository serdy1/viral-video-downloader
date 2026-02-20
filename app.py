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
    print(f"Analyzing URL: {url}")
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'socket_timeout': 15,
            'nocheckcertificate': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracing info...")
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({'error': 'Could not extract info'}), 400
            
            print(f"Info extracted for: {info.get('title')}")
            
            # Filter and prepare formats
            formats = []
            info_formats = info.get('formats', [])
            
            for f in info_formats:
                # Include combined formats or video-only formats that can be merged
                if f.get('vcodec') != 'none':
                    formats.append({
                        'ext': str(f.get('ext', '')),
                        'resolution': str(f.get('resolution') or f.get('format_note') or 'N/A'),
                        'filesize': f.get('filesize') or f.get('filesize_approx') or 0,
                        'format_id': str(f.get('format_id', '')),
                        'note': str(f.get('format_note') or f.get('ext', ''))
                    })
            
            # If still no formats, take the best available
            if not formats:
                formats.append({
                    'ext': str(info.get('ext', 'mp4')),
                    'resolution': 'Best Quality',
                    'filesize': info.get('filesize') or 0,
                    'format_id': 'best',
                    'note': 'Best available'
                })

            return jsonify({
                'title': str(info.get('title', 'Untitled')),
                'thumbnail': str(info.get('thumbnail', '')),
                'duration': info.get('duration') or 0,
                'view_count': info.get('view_count') or 0,
                'uploader': str(info.get('uploader', 'Unknown')),
                'formats': formats[:10] # Limit to 10 formats for performance
            })
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)