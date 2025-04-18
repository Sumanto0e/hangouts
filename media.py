import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
import requests

class Media:
    def __init__(self):
        self.font_path = "./fonts/Livvic-Regular.ttf"  # Pastikan folder fonts ada
        self.bg_path = "downloaded_bg.png"
        print("Media processor ready")

    def download_image(self):
        try:
            url = 'https://picsum.photos/720/1280/?random'
            r = requests.get(url, timeout=10)
            r.raise_for_status()  # Cek error HTTP
            with open(self.bg_path, 'wb') as f:
                f.write(r.content)
            print("Background downloaded")
        except Exception as e:
            print(f"Gagal download gambar: {e}")
            # Fallback ke gambar lokal jika ada
            if not os.path.exists(self.bg_path):
                self.bg_path = "default_bg.jpg"  # Siapkan file backup

    def process_image(self, text, author=None):
        # Bersihkan file lama
        for file in ["image.png", "ready.png"]:
            if os.path.exists(file):
                os.remove(file)
                
        # Proses teks
        text = textwrap.fill(text, width=35)
        try:
            # Buka gambar + efek
            img = Image.open(self.bg_path).filter(ImageFilter.GaussianBlur(10))
            img = ImageEnhance.Brightness(img).enhance(0.5)
            
            # Tambahkan teks
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(self.font_path, size=29)
            
            # Hitung posisi teks
            w, h = draw.textbbox((0, 0), text, font=font)[2:]
            draw.text(((720 - w) / 2, (1280 - h) / 2), text, fill="white", font=font)
            
            # Tambahkan author jika ada
            if author:
                author_text = f"@{author}"
                x, y = draw.textbbox((0, 0), author_text, font=font)[2:]
                draw.text(((720 - x) / 2, ((1280 / 2) + h) + 60), author_text, fill="white", font=font)
            
            img.save('ready.png')
            print("Gambar siap diposting")
        except Exception as e:
            print(f"Error proses gambar: {e}")
            raise  # Re-raise error untuk ditangkap di app.py