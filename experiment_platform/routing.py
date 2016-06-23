from channels import include
import chat
import forum
import waiting_room
channel_routing = [
include("chat.routing.channel_routing",path=r'^/chat/'),
include("forum.routing.channel_routing",path=r'^/forum/'),
include("waiting_room.routing.channel_routing",path=r'^'),


]

