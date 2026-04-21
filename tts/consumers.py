from channels.generic.websocket import AsyncWebsocketConsumer
import environ
import requests
import os
import json
import logging
from config.settings import BASE_DIR

logger = logging.getLogger("api")

environ.Env.read_env(os.path.join(BASE_DIR,'.env'))
env = environ.Env()

DEEPGRAM_URL = "https://api.deepgram.com/v1/speak?model=aura-2-thalia-en"
DEEPGRAM_API_KEY = env('DEEPGRAM_API_KEY')

headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "application/json"
}

audio_file_path = "output.wav"

class TTSConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        logger.info(f"{self.scope['user']} logged on to the {self.scope['path']}")
        self.room_group_name = 'tts'
        print(f"Connection from: {self.scope['client']}")
        print(f"Path: {self.scope['path']}")
        print(f"User: {self.scope['user']}")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        self.deepgram_connect(text='Hello')

        await self.accept()
    
    async def deepgram_connect(self,text):
        print("Audio creation starting...")
        with open(audio_file_path, 'wb') as file_stream:
            response = requests.post(DEEPGRAM_URL, headers=headers, json=text, stream=True)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file_stream.write(chunk) 
        print("Audio download complete")