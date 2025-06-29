from django.urls import re_path
from accounts.stores.consumers import ProfileConsumer

websocket_urlpatterns = [
    re_path(r'ws/profiles/$', ProfileConsumer.as_asgi()),
]
