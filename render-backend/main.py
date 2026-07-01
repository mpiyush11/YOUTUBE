import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(origins="*")

@app.route('/')
def home():
    return "YouTube Downloader API is running."

@app.route('/info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"error": "Video not found or private"}), 404

            formats = []
            seen_resolutions = set()

            for format in info.get('formats', []):
                height = format.get('height')
                if height and format.get('url'):
                    resolution = f"{height}p"
                    format_id = format.get('format_id')
                    ext = format.get('ext', 'mp4')
                    # Fixed: Proper string comparison
                    has_audio = format.get('acodec') != 'none'
                    
                    if resolution not in seen_resolutions:
                        seen_resolutions.add(resolution)
                        formats.append({
                            "resolution": resolution,
                            "format_id": format_id,
                            "ext": ext,
                            "has_audio": has_audio
                        })
            
            formats.sort(key=lambda x: int(x['resolution'].replace('p', '')), reverse=True)

            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "formats": formats
            })

    except Exception as e:
        # Fixed: Proper error handling syntax
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    format_id = request.args.get('format_id')
    
    if not url or not format_id:
        return jsonify({"error": "Missing URL or Format ID"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': format_id,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url')
            if direct_url:
                return jsonify({"download_url": direct_url})
            return jsonify({"error": "No link generated"}), 500
    except Exception as e:
        # Fixed: Proper error handling syntax
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
