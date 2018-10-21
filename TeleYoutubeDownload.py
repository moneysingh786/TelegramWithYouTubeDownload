from __future__ import unicode_literals
import telepot
import json
import youtube_dl
import os

"""
The YoutubeTelegramMerger class  have 2 methods as "send_video" and "send_audio"

1. "send_video" method will send the video to requested telegram users.
2. "send_audio" method will send the audio to requested telegram users.

"""


class YoutubeTelegramMerger:
    download_dir = ''

    def __init__(self, telegram_key, download_dir):
        self.telegram_key = telegram_key
        if download_dir:
            YoutubeTelegramMerger.download_dir = download_dir

    def index(self):
        if self.telegram_key:
            telegram_bot = telepot.Bot(self.telegram_key)
            return telegram_bot.getMe()
        else:
            return 'Invalid Telegram API Key'

    def get_updates(self):
        if self.telegram_key:
            telegram_bot = telepot.Bot(self.telegram_key)
            dd = telegram_bot.getMe()
            return telegram_bot.getUpdates()
        else:
            return 'Invalid Telegram API Key'

    def send_video(self, video_url, chat_id):
        """
        :param video_url:
        :param chat_id:
        :return:

        """
        print("vedio URL *** "+video_url)
        telegram_bot = telepot.Bot(self.telegram_key)
        data = {"title": "", "id": "", "url": "","status": "","message":""}
        ydl_opts = {
            'format': '22/best',
            'outtmpl': YoutubeTelegramMerger.download_dir+'//%(id)s.%(ext)s'
        }
        try:
            telegram_bot.sendChatAction(chat_id, "typing")
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                meta_details = ydl.extract_info(video_url)
            if meta_details['title']:
                data['title'] = meta_details['title']
            if meta_details['id']:
                data['id'] = meta_details['id']
            if YoutubeTelegramMerger.download_dir:
                data['url'] = YoutubeTelegramMerger.download_dir+'\\'+data['id']
            if data['url']:
                data['message'] = 'Download Completed'
                data['status'] = 'OK'
        except youtube_dl.utils.DownloadError:
            data['status'] = "ERROR"
            data['message'] = "Something went wrong unable to download audio"
            print(youtube_dl.utils.DownloadError)
            telegram_bot.sendMessage(chat_id, 'Unable to extract URL')
        if data['status'] == 'OK':
            file_path = str(data['url']+".mp4")
            print(file_path)
            if os.path.exists(file_path):
                telegram_bot.sendVideo(chat_id, open(file_path, "rb"))
            else:
                data['status'] = "ERROR"
                data['message'] = "Something went wrong unable to download audio"
        else:
            print(data['message'])
        return json.dumps(data)


    def my_hook(self,da):
        if da['status'] == 'finished':
            print('Done downloading, now converting ...')

    def send_audio(self, audio_url, chat_id):
        """
        :param audio_url:
        :param chat_id:
        :return:
        """
        telegram_bot = telepot.Bot(self.telegram_key)
        data = {"title": "", "id": "", "url": "", "status": "ERROR", "message": "Internal ERROR"}
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': YoutubeTelegramMerger.download_dir + '//%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self.my_hook],
        }
        telegram_bot.sendChatAction(chat_id, "typing")
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([audio_url])
                meta_details = ydl.extract_info(audio_url)
            if meta_details['title']:
                data['title'] = meta_details['title']
            if meta_details['id']:
                data['id'] = meta_details['id']
            if YoutubeTelegramMerger.download_dir:
                data['url'] = YoutubeTelegramMerger.download_dir
            if data['url']:
                data['message'] = 'Download Completed'
                data['status'] = 'OK'
        except youtube_dl.utils.DownloadError:
            data['status'] = "ERROR"
            data['message'] = "Something went wrong unable to download audio"
            telegram_bot.sendMessage(chat_id, 'Unable to extract URL')
        if data['status'] == 'OK':
            file_path = str(YoutubeTelegramMerger.download_dir + data['id'] + ".mp3")
            if os.path.exists(file_path):
                telegram_bot.sendAudio(chat_id, open(file_path, "rb"), title=data['title'])
            else:
                data['status'] = "ERROR"
                data['message'] = "Something went wrong unable to download audio"
        else:
            print(data['message'])
        return json.dumps(data)

    def send_message(self, message, chat_id):
        """
        :param message:
        :param chat_id:
        :return:
        """
        data = {"status": "OK", "message": ""}
        try:
            telegram_bot = telepot.Bot(self.telegram_key)
            telegram_bot.sendChatAction(chat_id, "typing")
            telegram_bot.sendMessage(chat_id, message)
            data['status'] = 'OK'
            data['message'] = ''
        except:
            data['status'] = 'ERROR'
            data['message'] = 'something went wrong unable to send message'
        return json.dumps(data)
