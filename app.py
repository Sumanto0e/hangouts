import os
import time
from datetime import datetime, timedelta
from twitter import Twitter
from media import Media
import traceback

class RateLimiter:
    def __init__(self):
        self.post_count = 0
        self.last_reset = datetime.now()
        
    def can_post(self):
        """Check if we can post without hitting rate limits"""
        if datetime.now() - self.last_reset >= timedelta(hours=1):
            self.post_count = 0
            self.last_reset = datetime.now()
        return self.post_count < 45

class MenfessBot:
    def __init__(self):
        self.tw = Twitter()
        self.media = Media()
        self.rate_limiter = RateLimiter()
        self.max_retries = 3
        self.cleanup_files = [
            'downloaded_bg.png',
            'image.png', 
            'ready.png'
        ]
        
    def cleanup(self):
        for file in self.cleanup_files:
            if os.path.exists(file):
                try: os.remove(file)
                except: pass
    
    def process_dm(self, dm):
        message = dm['message']
        sender_id = dm['sender_id']
        dm_id = dm['id']
        
        try:
            # Validasi pesan
            if not message or len(message) > 500:
                print(f"Pesan invalid dari {sender_id}")
                self.tw.delete_dm(dm_id)
                return False
                
            if "http://" in message or "https://" in message:
                print(f"Pesan mengandung URL dari {sender_id}")
                self.tw.delete_dm(dm_id)
                return False
                
            # [BARU] Cek hashtag #hangouts
            if "#hangouts" not in message.lower():
                print(f"Pesan tidak mengandung #hangouts dari {sender_id}")
                self.tw.delete_dm(dm_id)
                return False  # Hentikan proses jika tidak ada hashtag
            
            if not self.rate_limiter.can_post():
                print("Batas tweet per jam tercapai")
                time.sleep(3600)
                return False
                
            # Proses pesan
            include_author = "--s" in message
            if include_author:
                message = message.replace("--s", "").strip()
                screen_name = self.tw.get_user_screen_name(sender_id)
            else:
                screen_name = None
                
            # [OPTIONAL] Tambahkan hashtag otomatis
            if "#hangouts" not in message:
                message += "\n\n#hangouts"
                
            self.media.download_image()
            self.media.process_image(message, screen_name)
            
            if os.path.exists("ready.png"):
                self.tw.post_tweet("ready.png")
            else:
                self.tw.post_text_tweet(message)
                
            self.rate_limiter.post_count += 1
            self.tw.delete_dm(dm_id)
            print(f"Tweet dari {sender_id} diposting")
            return True
            
        except Exception as e:
            print(f"Gagal memproses DM: {str(e)}")
            traceback.print_exc()
            return False
        finally:
            self.cleanup()

    def run(self):
        print("Bot Menfess Berjalan")
        while True:
            try:
                dms = self.tw.read_dm()
                if not dms:
                    print("Tidak ada DM baru")
                    time.sleep(60)
                    continue
                    
                for dm in dms:
                    for attempt in range(self.max_retries):
                        if self.process_dm(dm):
                            break
                        time.sleep(5 * (attempt + 1))
                    else:
                        print(f"Gagal memproses DM setelah {self.max_retries} percobaan")
                        
                time.sleep(10)
                
            except Exception as e:
                print(f"ERROR: {str(e)}")
                traceback.print_exc()
                time.sleep(300)

if __name__ == "__main__":
    bot = MenfessBot()
    bot.run()