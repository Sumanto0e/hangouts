import tweepy
import constant
import time
from datetime import datetime
from typing import List, Dict, Optional

class Twitter:
    def __init__(self):
        self._api = self._init_api()
        self._last_api_call = datetime.now()
        self._rate_limit_delay = 1.1  # Minimal delay 1.1 detik antar API call

    def _init_api(self):
        """Inisialisasi koneksi Twitter API"""
        try:
            auth = tweepy.OAuthHandler(constant.CONSUMER_KEY, constant.CONSUMER_SECRET)
            auth.set_access_token(constant.ACCESS_TOKEN, constant.ACCESS_TOKEN_SECRET)
            return tweepy.API(
                auth,
                wait_on_rate_limit=True,
                retry_count=3,
                retry_delay=5
            )
        except Exception as e:
            print(f"Gagal inisialisasi API: {str(e)}")
            raise

    def _check_rate_limit(self):
        """Delay untuk menghindari rate limit"""
        elapsed = (datetime.now() - self._last_api_call).total_seconds()
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_api_call = datetime.now()

    def delete_dm(self, dm_id: str) -> bool:
        """Hapus DM setelah diproses"""
        print(f"Menghapus DM ID: {dm_id}")
        try:
            self._check_rate_limit()
            self._api.delete_direct_message(dm_id)
            return True
        except tweepy.errors.TweepyException as e:
            print(f"Gagal hapus DM {dm_id}: {str(e)}")
            return False

    def read_dm(self) -> List[Dict]:
        """Baca DM masuk terbaru"""
        print("Mengambil DM...")
        try:
            self._check_rate_limit()
            messages = self._api.get_direct_messages(count=50)
            
            processed_dms = []
            for msg in messages:
                if msg.message_create['target']['recipient_id'] == self._api.me().id_str:
                    processed_dms.append({
                        'id': msg.id,
                        'sender_id': msg.message_create['sender_id'],
                        'message': msg.message_create['message_data']['text']
                    })
            
            print(f"Berhasil mengambil {len(processed_dms)} DM")
            return processed_dms[::-1]  # Balik urutan agar yang terbaru di depan
            
        except tweepy.errors.TweepyException as e:
            print(f"Error baca DM: {str(e)}")
            return []

    def post_tweet(self, media_path: str, text: Optional[str] = None) -> bool:
        """Posting tweet dengan media gambar"""
        print(f"Posting tweet dengan gambar: {media_path}")
        try:
            self._check_rate_limit()
            if text:
                self._api.update_with_media(media_path, status=text)
            else:
                self._api.update_with_media(media_path)
            return True
        except tweepy.errors.TweepyException as e:
            print(f"Gagal posting tweet: {str(e)}")
            return False

    def post_text_tweet(self, text: str) -> bool:
        """Posting tweet text saja"""
        print(f"Posting text tweet: {text[:50]}...")
        try:
            self._check_rate_limit()
            self._api.update_status(text)
            return True
        except tweepy.errors.TweepyException as e:
            print(f"Gagal posting text tweet: {str(e)}")
            return False

    def get_user_screen_name(self, user_id: str) -> Optional[str]:
        """Dapatkan username dari ID pengguna"""
        print(f"Mencari username untuk ID: {user_id}")
        try:
            self._check_rate_limit()
            user = self._api.get_user(user_id=user_id)
            return user.screen_name
        except tweepy.errors.TweepyException as e:
            print(f"Gagal dapatkan username: {str(e)}")
            return None

    def verify_credentials(self) -> bool:
        """Verifikasi koneksi API"""
        try:
            self._check_rate_limit()
            user = self._api.verify_credentials()
            print(f"Terhubung sebagai: @{user.screen_name}")
            return True
        except tweepy.errors.TweepyException as e:
            print(f"Gagal verifikasi: {str(e)}")
            return False
