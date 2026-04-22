from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
   re_path(r'ws/tts', consumers.TTSConsumer.as_asgi()),
   re_path(r'ws/cartesia/tts', consumers.CartAsiaConsumer.as_asgi()),

]