from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter
import chat.routing

''' main entry of routing system
    protcoltype router Automatically maps http request to 
    standard django view if no Specfic http method'''
application = ProtocolTypeRouter({
 # AuthMiddlewareStack to support Django authentication allowing you to user details within the consmer
 'websocket': AuthMiddlewareStack(
    URLRouter(
        chat.routing.websocket_urlpatterns
    )
 ),
})