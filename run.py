import os
import yt_dlp
import re
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

UPLOAD_FOLDER = 'descargas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def descargar_audio(url, output_folder=UPLOAD_FOLDER):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'audio')
            
            # Limpiar caracteres especiales
            video_title = re.sub(r'[^\w\-_ ]', '', video_title).strip()
            file_path = os.path.join(output_folder, f"{video_title}.mp3")
            
            return file_path, video_title
    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = None
    archivo = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            file_path, result = descargar_audio(url)
            if file_path:
                archivo = os.path.basename(file_path)
                mensaje = f"¡Descarga completada! Archivo: {archivo}"
            else:
                mensaje = f"Error: {result}"
    
    return render_template('index.html', mensaje=mensaje, archivo=archivo)

@app.route('/descargas/<filename>')
def descargar_archivo(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Archivo no encontrado", 404

if __name__ == '__main__':
    app.run(debug=True)
