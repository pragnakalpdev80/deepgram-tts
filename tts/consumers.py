from channels.generic.websocket import AsyncWebsocketConsumer
import environ
import requests
import os
import json
import logging
import websockets
from datetime import datetime
from config.settings import BASE_DIR

logger = logging.getLogger("api")

environ.Env.read_env(os.path.join(BASE_DIR,'.env'))
env = environ.Env()

DEEPGRAM_API_KEY = env('DEEPGRAM_API_KEY')

class TTSConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        logger.info(f"{self.scope['user']} logged on to the {self.scope['path']}")
        self.room_group_name = 'tts'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        self.audio_file_path = f"output_{self.scope['user']}_{datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")}.wav"
        self.sample_rate = 48000

        deepgram_url = f'wss://api.deepgram.com/v1/speak?model=aura-2-thalia-en&encoding=linear16&sample_rate={self.sample_rate}'
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            self.dg_connect = await websockets.connect(deepgram_url, additional_headers=headers)
            logger.info(f"{self.scope['user']} connected to deepgram")
        except Exception as e:
            logger.error(e)
            await self.close()
        await self.accept()
    
    async def disconnect(self, code):
        logger.info(f"WebSocket disconnected with code {code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data = None, bytes_data = None):
        if text_data:
            logger.info(f"{self.scope['user']} sent {text_data}")
            await self.dg_connect.send(json.dumps({"type": "Speak", "text": text_data}))
            await self.dg_connect.send(json.dumps({"type": "Flush"}))
            
