from yt_dlp import YoutubeDL

def obtener_miniatura(url):
    ydl_opts = {
        'skip_download': True,  # No descargaremos el video, solo obtenemos la info
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        # Extraemos la URL de la miniatura
        miniatura_url = info_dict.get("thumbnail")
        return miniatura_url

# URL del video de YouTube
video_url = "https://youtu.be/UBYyOaj6Hio?si=057nkBl_RJicp9Nl"

try:
    miniatura_url = obtener_miniatura(video_url)
    print(f"La URL de la miniatura es: {miniatura_url}")
except Exception as e:
    print(f"Error al obtener la miniatura: {e}")
