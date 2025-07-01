from flask import Flask, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/api/info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [{
                'format_id': f['format_id'],
                'ext': f['ext'],
                'format': f['format'],
                'filesize': f.get('filesize', 0)
            } for f in info['formats'] if f.get('filesize')]

            return jsonify({
                'title': info.get('title'),
                'channel': info.get('uploader'),
                'thumbnail': info.get('thumbnail'),
                'formats': formats
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    url = request.json.get('url')
    format_id = request.json.get('format_id')
    if not url or not format_id:
        return jsonify({'error': 'Missing URL or format_id'}), 400

    output_filename = 'video.%(ext)s'
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_filename
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find the downloaded file
        for file in os.listdir('.'):
            if file.startswith('video.'):
                response = send_file(file, as_attachment=True)
                os.remove(file)
                return response

        return jsonify({'error': 'File not found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🚀 This line is CRUCIAL for Render to run it properly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
