from channels.generic.websocket import AsyncWebsocketConsumer
import environ
import requests
import asyncio
import wave
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

        self.audio_file_path = f"media/{self.scope['user']}_{datetime.now().strftime("%Y%m%d%H%M%S%z")}.wav"
        self.file = wave.open(self.audio_file_path, 'wb')
        self.sample_rate = 24000
        self.file.setnchannels(1)
        self.file.setsampwidth(2)
        self.file.setframerate(self.sample_rate)

        deepgram_url = f'wss://api.deepgram.com/v1/speak?model=aura-2-thalia-en&encoding=linear16&sample_rate={self.sample_rate}'
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            self.dg_connect = await websockets.connect(deepgram_url, additional_headers=headers)
            logger.info(f"{self.scope['user']} connected to deepgram")
            self.dg_recieve = asyncio.create_task(self.deepgram_receive())
        except Exception as e:
            logger.error(f"Deepgram server error: {e}")
            await self.close()
        await self.accept()
    
    async def disconnect(self, code):
        logger.info(f"TTS WebSocket disconnected with code {code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if self.dg_connect:
            await self.dg_connect.send(json.dumps({"type": "Close"}))
            logger.info(f"Deepgram WebSocket Disconnected.")

    async def receive(self, text_data = None, bytes_data = None):
        if text_data:
            logger.info(f"{self.scope['user']} sent {text_data}")
            await self.dg_connect.send(json.dumps({"type": "Speak", "text": text_data}))
            await self.dg_connect.send(json.dumps({"type": "Flush"}))
            logger.info(f"message sent to Deepgram")
            
    async def deepgram_receive(self):  
        try: 
            async for data in self.dg_connect:
                if isinstance(data, bytes):
                    logger.info(f"Chunks Recieved: {data}")
                    self.file.writeframes(data)
                    await self.send(bytes_data=data)
                else:
                    logger.info(f"{data}")
                    await self.send(text_data=data)
        except Exception as e:
            logger.log(f"Unexpected Error: {e}")            

                      
