# Viral Video Downloader

Bu proje, YouTube, Instagram, Pinterest, Reddit ve Twitter gibi sosyal medya platformlarından video ve fotoğraf indirmenizi sağlayan bir web uygulamasıdır. YT-DLP kütüphanesini kullanarak güçlü ve güvenilir indirme özellikleri sunar.

## Özellikler

- **Desteklenen Platformlar**: YouTube, Instagram, Pinterest, Reddit, Twitter
- **Format Seçenekleri**: MP4, MP3, WebM ve daha fazlası
- **Responsive Tasarım**: Mobil ve masaüstü uyumlu Bootstrap arayüzü
- **Kolay Kullanım**: Sadece URL yapıştırın ve indirin

## Kurulum ve Çalıştırma

1. Python ortamını yapılandırın (venv önerilir).
2. Gerekli paketleri yükleyin:
   ```
   pip install yt-dlp flask
   ```
3. Uygulamayı çalıştırın:
   ```
   python app.py
   ```
4. Tarayıcıda `http://localhost:5000` adresine gidin.

## Kullanım

1. Ana sayfada indirmek istediğiniz medyanın URL'sini yapıştırın.
2. İstenen formatı seçin (örneğin MP4 için video, MP3 için ses).
3. "Download" düğmesine tıklayın.
4. İndirme hazır olduğunda, bağlantıya tıklayarak dosyayı indirin.

## Örnek Kullanım

```python
import yt_dlp

def download_video(url, output_dir, format_choice='best'):
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'format': format_choice,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
```

## Lisans

Bu proje açık kaynak kodludur ve MIT lisansı altında yayınlanmıştır.