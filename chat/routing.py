from channels.staticfiles import StaticFilesConsumer
from . import consumers

channel_routing = {
    # This makes Django serve static files from settings.STATIC_URL, similar
    # to django.views.static.serve. This isn't ideal (not exactly production
    # quality) but it works for a minimal example.
    'http.request': StaticFilesConsumer(),

    # Wire up websocket channels to our consumers:
    'websocket.connect': consumers.ws_chat_connect,
    'websocket.receive': consumers.ws_chat_receive,
    'websocket.disconnect': consumers.ws_chat_disconnect,
}
