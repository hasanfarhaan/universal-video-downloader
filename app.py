from flask import Flask, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/api/info', methods=['POST'])
def get_info():
    url = request.json.get('url')
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
            'title': info['title'],
            'channel': info.get('uploader', ''),
            'thumbnail': info['thumbnail'],
            'formats': formats
        })

@app.route('/api/download', methods=['POST'])
def download():
    url = request.json.get('url')
    format_id = request.json.get('format_id')
    output_path = 'video.%(ext)s'

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    downloaded = next((f for f in os.listdir('.') if f.startswith('video.')), None)
    return send_file(downloaded, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
