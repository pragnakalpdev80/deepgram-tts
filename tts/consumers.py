from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import environ
import base64
import asyncio
import wave
import os
import audioop
import json
import logging
import websockets
from datetime import datetime
from config.settings import BASE_DIR
import uuid
from urllib.parse import parse_qs

from .models import TTSModels

logger = logging.getLogger("api")

environ.Env.read_env(os.path.join(BASE_DIR,'.env'))
env = environ.Env()

DEEPGRAM_API_KEY = env('DEEPGRAM_API_KEY')
CARTESIA_API_KEY = env('CARTESIA_API_KEY')

class TTSConsumer(AsyncWebsocketConsumer):
    
    @database_sync_to_async
    def model_is_valid(self, model):
        try:
            ttsmodel = TTSModels.objects.select_related("tool").filter(name=model).first()
            return ttsmodel.tool.name == 'Deepgram'
        except Exception as e:
            return False

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        is_valid = await self.model_is_valid(query_string)
        logger.info(f"{self.scope['user']} logged on to the {self.scope['path']}")
        self.room_group_name = 'tts'
        
        if not is_valid:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.audio_file_path = f"media/{self.scope['user']}_{datetime.now().strftime("%Y%m%d%H%M%S%z")}.wav"
        self.file = wave.open(self.audio_file_path, 'wb')
        self.model = query_string
        self.sample_rate = 8000
        self.file.setnchannels(1)
        self.file.setsampwidth(4)
        self.file.setframerate(self.sample_rate)

        deepgram_url = f'wss://api.deepgram.com/v1/speak?model={self.model}&encoding=mulaw&sample_rate={self.sample_rate}'
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
        try:
            self.file.close()
        except:
            pass
        try:
            if self.dg_connect:
                await self.dg_connect.send(json.dumps({"type": "Close"}))
                logger.info(f"Deepgram WebSocket Disconnected.")
        except:
            pass

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
                    try:
                        linear_data=audioop.ulaw2lin(data,2)
                    except Exception as e:
                        print(e)
                    self.file.writeframesraw(linear_data)
                    await self.send(bytes_data=linear_data)

                else:
                    logger.info(f"{data}")
                    # await self.send(text_data=data)
        except Exception as e:
            logger.log(f"Unexpected Error: {e}")            

                      
class CartAsiaConsumer(AsyncWebsocketConsumer):
    
    @database_sync_to_async
    def model_is_valid(self, model):
        try:
            ttsmodel = TTSModels.objects.select_related("tool").filter(name=model).first()
            return ttsmodel.tool.name == 'Cartesia'
        except Exception as e:
            return False
        
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        is_valid = await self.model_is_valid(query_string)
        
        logger.info(f"{self.scope['user']} logged on to the {self.scope['path']}")
        self.room_group_name = 'tts'
        
        if not is_valid:
            await self.close()
            return
          
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.audio_file_path = f"media/{self.scope['user']}_{datetime.now().strftime("%Y%m%d%H%M%S%z")}.wav"
        self.file = wave.open(self.audio_file_path, 'wb')
        self.sample_rate = 8000
        self.model_id = query_string
        self.voice_id = "a0e99841-438c-4a64-b679-ae501e7d6091"
        self.file.setnchannels(1)
        self.file.setsampwidth(4)
        self.file.setframerate(self.sample_rate)

        deepgram_url = f'wss://api.cartesia.ai/tts/websocket?cartesia_version=2026-03-01'
        headers = {
            "X-API-Key": CARTESIA_API_KEY,
        }

        try:
            self.dg_connect = await websockets.connect(deepgram_url, additional_headers=headers)
            logger.info(f"{self.scope['user']} connected to cartesia")
            self.dg_recieve = asyncio.create_task(self.cartesia_receive())
        except Exception as e:
            logger.error(f"Cartesia server error: {e}")
            await self.close()
        await self.accept()
    
    async def disconnect(self, code):
        logger.info(f"TTS WebSocket disconnected with code {code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        try:
            self.file.close()
        except:
            pass

        try:
            if self.dg_connect:
                self.dg_connect.close(code)
                logger.info(f"Cartesia WebSocket Disconnected.")
        except:
            pass
        
    async def receive(self, text_data = None, bytes_data = None):
        if text_data:
            logger.info(f"{self.scope['user']} sent {text_data}")
            data={
                "model_id": self.model_id,
                "transcript": text_data,
                "voice": {
                    "mode": "id",
                    "id": self.voice_id
                },
                "language": "en",
                "context_id": str(uuid.uuid4()),
                "output_format": {
                    "container": "raw",
                    "encoding": "pcm_mulaw",
                    "sample_rate": self.sample_rate
                },
                "add_timestamps": True,
                "continue": False
            }
            await self.dg_connect.send(json.dumps(data))
            logger.info(f"message sent to Cartesia")
            
    async def cartesia_receive(self):  
        try: 
            async for data in self.dg_connect:
                if isinstance(data, str):
                    logger.info(f"Chunks Recieved: {data}")
                    data_dict = json.loads(data)
                    if data_dict["type"] == "chunk":
                        decoded_data = base64.b64decode(data_dict["data"])
                        # print(decoded_data)
                        linear_data = audioop.ulaw2lin(decoded_data,4)
                        # print(linear_data)
                        await self.send(bytes_data=linear_data)
                        self.file.writeframesraw(linear_data)
                        logger.info(f"Chunks Recieved: {data}")
                    else:
                        logger.info(f"{data}")
                        # await self.send(text_data=data)
        except Exception as e:
            logger.log(f"Unexpected Error: {e}")   