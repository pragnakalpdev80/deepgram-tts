from channels.generic.websocket import AsyncWebsocketConsumer
import environ
from deepgram import DeepgramClient
# from typing import Dict

import os

env = environ.Env()

class TTSConsumer(AsyncWebsocketConsumer):
    pass
    # deepgram = DeepgramClient(os.getenv('DEEPGRAM_API_KEY'),)

    # async def connect(self):
    #     with deepgram.speak.v1.connect(
    #         model="aura-2-thalia-en",
    #         encoding="linear16",
    #         sample_rate=48000
    #     ) as dg_connection:
    #         pass
  