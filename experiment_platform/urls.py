from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('experiment.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^chats/', include('experiment.urls')),
    #url(r'^',include('chat.urls')),
    url(r'^chat/',include('chat.urls')),
    url(r'^forum/',include('forum.urls')),
    
]
