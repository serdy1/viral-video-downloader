import yt_dlp
import sys

def test_analyze(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Title: {info.get('title')}")
            print(f"Uploader: {info.get('uploader')}")
            
            formats_count = 0
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    formats_count += 1
            print(f"Found {formats_count} combined formats")
            
            if formats_count == 0:
                print("Warning: No combined formats found. Your filter might be too strict.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_analyze(sys.argv[1])
    else:
        # Test with a common video
        test_analyze("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
