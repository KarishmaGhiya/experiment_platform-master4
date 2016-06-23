from django.conf.urls import include, url
from waiting_room import views



urlpatterns = [
    url(r'^$',  views.wait_home, name='wait_home'),
   
]
