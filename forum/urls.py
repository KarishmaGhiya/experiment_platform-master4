from django.conf.urls import include, url
#from . import chat.views
import views

urlpatterns = [
    url(r'^$',  views.about, name='about'),
    url(r'^new/$', views.new_discussion, name='new_discussion'),
    url(r'^(?P<label>[\w-]{,50})/$', views.discussion_forum, name='discussion_forum'),
]
