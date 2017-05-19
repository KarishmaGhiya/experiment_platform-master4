from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    #url(r'^consent/',views.consent,name='consent'),
    url(r'^nickname/',views.nickname,name='nickname'),
    #url(r'^chats/', views.home_page, name='home_page'),
    url(r'^wait/',views.before_task,name='wait_before_task'),
    url(r'^wait/',views.wait_room,name='waiting_room'),
    url(r'^chatapp/',views.chatapp,name='chatapp'),
    url(r'^forumapp/',views.forumapp,name='forumapp'),
    url(r'^survey/',views.survey,name='survey'),
    url(r'^finish/',views.finish,name='finish'),
    url(r'^error/',views.error_page,name='error'),
]
