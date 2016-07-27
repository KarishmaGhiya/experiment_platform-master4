import json
from channels import Channel
from django.contrib.sessions.models import Session
from channels.auth import http_session, http_session_user, channel_session_user, channel_session_user_from_http

from .models import WaitRoom, WaitUser
from experiment.models import ExpUser, Crowd, Crowd_Members 
import re
import json
import logging
from channels import Group
from channels.sessions import channel_session
import redis
from random import randint

redis_conn = redis.Redis("localhost", 6379)
log = logging.getLogger(__name__)
@channel_session_user_from_http
@channel_session
def wait_connect(message):
    try:
	    log.debug('In the try block of ws_connect')#added by me
        #you can do a check for message path \wait if you want
	    title = "wait"
	    wait_room, created = WaitRoom.objects.get_or_create(title=title)
    
    except WaitRoom.DoesNotExist:
        log.debug('ws room does not exist title=%s', title)
        return

    #log.debug('wait user.username %s',message.user.username)


    log.debug('wait connect discussion=%s', wait_room.title)
    Group('wait-'+title, channel_layer=message.channel_layer).add(message.reply_channel)
    message.channel_session['wait_room'] = wait_room.title 
    
    #workerId = 'testworker' + str(randint(1,1000))
    #message.channel_session['worker_id'] = workerId
    #workerId = message.user.username

    log.debug('wait connect room=%s', wait_room.title)
    wait_user,created = wait_room.users.get_or_create(user=message.user)
    wait_user.is_active = 1
    wait_user.save()
    if created:
        wait_room.numwait += 1
        wait_room.save()
    
    userlist = WaitUser.objects.filter(wait_room=wait_room,is_active=1)
    log.debug('wait connect numusers=%s', 
        len(userlist))
    if len(userlist)>=3:
           
        #check crowd id of empty crowd
        which_crowd = Crowd.objects.Crowd_which_assign()

        log.debug("which_crowd=%d",which_crowd)
        crowd =  Crowd.objects.get(id = which_crowd)##
        cohortid = randint(1,100000)

        for u in userlist:
            crowd.members.create(user=u.user,crowd=crowd,cohort_id=cohortid)
            eu = ExpUser.objects.get(user=u.user)
            eu.expstage = "task"
	    #eu.secret_code = randint(1,100000)
            eu.save()
            u.is_active = 0
            u.save()		
		

        log.debug("3 objects created in crowd_members..check your database now")
		#update the message m with the url to be directed onto == url -label== room(crowd-id) == url= chat/forum
		#fetch the object for which crowd & look up the object if it has chat/forum
        t = {}		
        if crowd.communication == '_forum':
            t['url']='http://crowdps.umd.edu/forum/room'
        elif crowd.communication == '_chat':
            t['url']='http://crowdps.umd.edu/chat/room'
        t['url'] += str(which_crowd)
	log.debug(json.dumps(t))
        Group('wait-'+title, channel_layer=message.channel_layer).send({'text': json.dumps(t)})
    log.debug('after if & group')


@channel_session_user
@channel_session
def wait_receive(message):


    mymessage = message.content['text']
    try:
        myuser = message.user
        u = ExpUser.objects.get(user=myuser)
        #log.debug("gets user from expuser %s",u.expstage)
        if u.expstage=="task":
            #log.debug("right before crowd members")
            cm = Crowd_Members.objects.get(user=myuser)
            #log.debug("right after crowd members")
            #log.debug("gets com %s",cm.crowd.communication)
            if cm.crowd.communication == '_forum':
                mymessage ='http://crowdps.umd.edu/forum/room'+str(cm.crowd.id)
            elif cm.crowd.communication == '_chat':
                mymessage ='http://crowdps.umd.edu/chat/room'+str(cm.crowd.id)
            #log.debug("gets url %s",mymessage)
            t = {'url':mymessage,
                'users':[myuser.username]
                }
            message.reply_channel.send({
                "text":json.dumps(t),
            })
        else:
            pass
            #mymessage  = "continue to wait"

    except:
        log.debug("problem getting user %s",myuser)

	

@channel_session_user
@channel_session
def wait_disconnect(message):
    try:
        title = message.channel_session['wait_room']
        log.debug('wait disconnect from room %s',title)
        wait_room = WaitRoom.objects.get(title=title)
        log.debug('wait disconnect user.username %s',message.user.username)
        #wait_user = WaitUser.objects.get(worker_id=message.user.username)
        #wait_user.leave_wait()
        wait_room.numwait = max(0,wait_room.numwait-1)
        wait_room.save()
        
        Group('wait-'+title, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, WaitRoom.DoesNotExist):
        pass





