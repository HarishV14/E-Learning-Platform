from django.urls import re_path
from . import consumers

#/ws/ to differentiate them from standard Http URLS 
websocket_urlpatterns = [
    re_path(r'ws/chat/room/(?P<course_id>\d+)/$', consumers.ChatConsumer),
]