from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
	re_path("ws/game", consumers.GameConsumer.as_asgi()),
	re_path(r"ws/multiplayer/(?P<room_name>\w+)", consumers.MultiplayerGameConsumer.as_asgi()),
	
]