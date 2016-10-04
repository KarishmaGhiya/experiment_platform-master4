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
    
   

    log.debug('wait connect room=%s', wait_room.title)
    wait_user,created = wait_room.users.get_or_create(user=message.user)
    wait_user.is_active = 1
    wait_user.save()
    if created:
        wait_room.numwait += 1
        wait_room.save()
    #check that the person is not assigned to the crowd
    userlist = WaitUser.objects.filter(wait_room=wait_room,is_active=1)
    log.debug('wait connect numusers=%s',len(userlist))
    
    #To check if a crowd is open , size>30
    which_crowd = Crowd.objects.Crowd_assign()#write another function that only checks which crowd
    log.debug("which_crowd=%d",which_crowd)
    #crowd =  Crowd.objects.get(id = which_crowd)
    if which_crowd > 0:
	log.debug("which crowd=%d",which_crowd)
	crowd = Crowd.objects.get(id = which_crowd)
	count_existing = Crowd_Members.objects.filter(crowd=crowd).count()
	if count_existing < 30:
		#count_existing = Crowd_Members.objects.filter(crowd=crowd).count()
		log.debug("count_existing=%d",count_existing)
		member_num = count_existing
		cohortid = (count_existing)/3
		log.debug("cohort id=%d",cohortid)
		crowd.members.create(user=wait_user.user,crowd=crowd,cohort_id=cohortid,member_num=member_num)
		eu = ExpUser.objects.get(user=wait_user.user)
        	eu.expstage = "task"
		eu.save()
		wait_user.is_active = 0
		wait_user.save()
		'''t = {}      	
		t['notification'] = 'check status'
		log.debug(json.dumps(t))
        	Group('wait-'+title, channel_layer=message.channel_layer).send({'text': json.dumps(t)})'''
    #If no crowd open then do this
    else:
      log.debug("which crowd in else=%d",which_crowd)
      if len(userlist)>=3:
        #have to divide this by %3   
        for i in range(0,len(userlist),3):
		if (i+3) <= len(userlist) :
			sub_list = userlist[i:i+3]
			i = i+3
			#check crowd id of empty crowd
        		which_crowd = Crowd.objects.Crowd_which_assign()
        		log.debug("which_crowd=%d",which_crowd)
        		crowd =  Crowd.objects.get(id = which_crowd)     		
			

	        	for u in sub_list:
			    count_existing = Crowd_Members.objects.filter(crowd=crowd).count()
			    member_num = count_existing
			    cohortid = (count_existing)/3
	        	    crowd.members.create(user=u.user,crowd=crowd,cohort_id=cohortid,member_num=member_num)
	        	    eu = ExpUser.objects.get(user=u.user)
	        	    eu.expstage = "task"
			   
	        	    eu.save()
	        	    u.is_active = 0
	        	    u.save()		
		

        		log.debug("3 objects created in crowd_members..check your database now")
			#update the message m with the url to be directed onto == url -label== room(crowd-id) == url= chat/forum
			#fetch the object for which crowd & look up the object if it has chat/forum
        		

	    	else:
			break
	#userlist = WaitUser.objects.filter(wait_room=wait_room,is_active=1)
	#if len(userlist) < 3 :
	#break
    t = {}      	
    t['notification'] = 'check status'
    log.debug(json.dumps(t))
    Group('wait-'+title, channel_layer=message.channel_layer).send({'text': json.dumps(t)})



@channel_session_user
@channel_session
def wait_receive(message):


    mymessage = message.content['text']
    try:
        myuser = message.user
        u = ExpUser.objects.get(user=myuser)
        #log.debug("gets user from expuser %s",u.expstage)
	'''
	If status = task then redirect -not checking what message got from client js??
	'''
        if u.expstage=="task":
            #log.debug("right before crowd members")
            cm = Crowd_Members.objects.get(user=myuser)
            #log.debug("right after crowd members")
            #log.debug("gets com %s",cm.crowd.communication)
            if cm.crowd.communication == '_forum':
		#mymessage = '127.0.0.1:80/forum/room'+str(cm.crowd.id)
                mymessage ='http://crowdps.umd.edu/forum/room'+str(cm.crowd.id)
            elif cm.crowd.communication == '_chat':
		#mymessage = '127.0.0.1:80/chat/room'+str(cm.crowd.id)                
		mymessage ='http://crowdps.umd.edu/chat/room'+str(cm.crowd.id)
            #log.debug("gets url %s",mymessage)
            t = {'url':mymessage,
                'users':[myuser.username],
		'notification':'redirect to url'
                }
            message.reply_channel.send({
                "text":json.dumps(t),
            })
        else:
            pass
          

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
        
        wait_room.numwait = max(0,wait_room.numwait-1)
        wait_room.save()
        
        Group('wait-'+title, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, WaitRoom.DoesNotExist):
        pass





