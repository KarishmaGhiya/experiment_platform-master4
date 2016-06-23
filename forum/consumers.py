import re
import json
import logging
from channels import Group
from channels.sessions import channel_session
from .models import Discussion, Statement, Vote
from chat.models import Room
from experiment.models import ExpUser
from channels.auth import http_session, http_session_user, channel_session_user, channel_session_user_from_http


log = logging.getLogger(__name__)

@channel_session_user_from_http
@channel_session
def ws_connect(message):
    # Extract the discussion-label from the message. This expects message.path to be of the
    # form forum/{label}/, and finds a Discussion if the message path is applicable,
    # and if the Discussion exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
	log.debug('In the try block of ws_connect')#added by me
        prefix, label = message['path'].decode('ascii').strip('/').split('/')
#	if prefix != 'forum' and prefix != 'chat':
	if prefix != 'forum':
            log.debug('invalid ws path=%s', message['path'])
	    
            return
	if prefix == 'forum':
	        discussion = Discussion.objects.get(label=label)
#	if prefix =='chat':
#		room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Discussion.DoesNotExist:
        log.debug('ws discussion does not exist label=%s', label)
        return
#    except Room.DoesNotExist:
#        log.debug('ws room does not exist label=%s', label)
#        return

#    if prefix == 'chat':
#	log.debug('chat connect room=%s client=%s:%s', room.label, message['client'][0], message['client'][1])
#	# Need to be explicit about the channel layer so that testability works
#        # This may be a FIXME?
#        Group('chat-'+label, channel_layer=message.channel_layer).add(message.reply_channel)
#        message.channel_session['room'] = room.label 
    if prefix == 'forum':
	log.debug('forum connect discussion=%s client=%s:%s', discussion.label, message['client'][0], message['client'][1])
        # Need to be explicit about the channel layer so that testability works
        # This may be a FIXME?
        Group('forum-'+label, channel_layer=message.channel_layer).add(message.reply_channel)
        message.channel_session['discussion'] = discussion.label 	
    

@channel_session_user
@channel_session
def ws_receive(message):
  if 'discussion' in message.channel_session:
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['discussion']
        discussion = Discussion.objects.get(label=label)
    except KeyError:
        log.debug('no discussion-forum in channel_session')
        return
    except Discussion.DoesNotExist:
        log.debug('recieved message, buy discussion does not exist label=%s', label)
        return


    try:
        expuser = ExpUser.objects.get(user=message.user)
    except KeyError:
        log.debug('problem getting username')
        return
    except ExpUser.DoesNotExist:
        log.debug('recieved message, but user does not exist label=%s', label)
        return


    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return
    
    ## check whether it is acceptable format
#    if set(data.keys()) != set(('handle', 'message','isreply','parentid')):
    
    #if set(data.keys()) != set(('handle', 'msg_type')):
    #    log.debug("ws message unexpected format data=%s", data)
    #    return

    if data:
    
        if data['msg_type'] == 'vote':
            log.debug('vote handle=%s value=%s', 
            expuser.nickname, data['value'])
        
            statement = Statement.objects.get(id=data['id'])
            m0 = statement.as_dict()
            log.debug('vote id=%s, score=%s, ups=%s, downs=%s',statement.id,statement.score,statement.ups,statement.downs)
            
            ndata = {'user':message.user,'handle':expuser.nickname,'statement':statement,'value':data['value']}
            vote = Vote.objects.create(**ndata)
            vote = vote.new_vote()
            #m = Vote.objects.create(data['handle'],statement,data['value']) # NEED TO FIX HERE
            #vote = Vote.create(handle=data['handle'],
            #               statement=statement,
            #               value=data['value'])
            #vote.save()
            m = statement.update_score()
            m['msg_type'] = 'vote'
            log.debug('vote score=%s', 
            m['score'])

            # See above for the note about Group
            Group('forum-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(m)})

        else:
            log.debug('chat message handle=%s message=%s', 
            expuser.nickname, data['message'])


            
#        if data["isreply"]==0:
#            parent = discussion
#            m = discussion.statements.create(data['handle'],data['message'],parent,data['isreply'],data['parentid'])  
#        else:
#            parent = discussion.statements.get(id=data['parentid'])
#            m = discussion.statements.create(data['handle'],data['message'],parent,data['isreply'],data['parentid']) 
        
            parent = None
            log.debug(data['parentid'])
            if data['parentid']!=0:
                parent = discussion.statements.get(id=data['parentid'])
                log.debug(parent.id)
            data['parent'] = parent
            data.pop("msg_type",None)
            data['user'] = message.user
            data['handle'] = expuser.nickname
            m = discussion.statements.create(**data) # NEED TO FIX HERE

            # See above for the note about Group
            Group('forum-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})

#  if 'room' in message.channel_session:
#     # Look up the room from the channel session, bailing if it doesn't exist
#    try:
#        label = message.channel_session['room']
#        room = Room.objects.get(label=label)
#    except KeyError:
#        log.debug('no room in channel_session')
#        return
#    except Room.DoesNotExist:
#        log.debug('recieved message, buy room does not exist label=%s', label)
#        return
#
#    # Parse out a chat message from the content text, bailing if it doesn't
#    # conform to the expected message format.
#    try:
#        data = json.loads(message['text'])
#    except ValueError:
#        log.debug("ws message isn't json text=%s", text)
#        return
#    
#    if set(data.keys()) != set(('handle', 'message','isreply','parentid')):
#        log.debug("ws message unexpected format data=%s", data)
#        return
#
#    if data:
#        log.debug('chat message room=%s handle=%s message=%s id=%s', 
#            room.label, data['handle'], data['message'])
#        m = room.messages.create(**data) # NEED TO FIX HERE
#
#        # See above for the note about Group
#        Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})

@channel_session_user
@channel_session
def ws_disconnect(message):
  if 'discussion' in message.channel_session:
    try:
        label = message.channel_session['discussion']
        discussion = Discussion.objects.get(label=label)
        Group('forum-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Discussion.DoesNotExist):
        pass
#  if 'room' in message.channel_session:
#     try:
#        label = message.channel_session['room']
#        room = Room.objects.get(label=label)
#        Group('chat-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
#     except (KeyError, Room.DoesNotExist):
#        pass
