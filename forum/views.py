import random
import string
from django.db import transaction
from django.shortcuts import render, redirect
from django.core import serializers
import haikunator
from .models import Discussion, Statement
from experiment.models import Crowd_Members, Crowd, ProblemHint, ProfileHint,UserProfile, Profile 
import logging

log = logging.getLogger(__name__)

def about(request):
    return render(request, "forum/about.html")

def new_discussion(request):
    """
    Randomly create a new discussion, and redirect to it.
    """
    new_discussion = None
    while not new_discussion:
        with transaction.atomic():
            h = haikunator.Haikunator()
            label = h.haikunate()
            #label = haikunator.haikunate()
            if Discussion.objects.filter(label=label).exists():
                continue
            new_discussion = Discussion.objects.create(label=label)
    return redirect(discussion_forum, label=label)

def discussion_forum(request, label):
    """
    Room view - show the room, with latest messages.

    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    if request.user.is_authenticated(): 
        # If the room with the given label doesn't exist, automatically create it
        # upon first visit (a la etherpad).
        discussion, created = Discussion.objects.get_or_create(label=label)

        # get problem 
        try:
            cm = Crowd_Members.objects.get(user=request.user)
        except Crowd_Members.DoesNotExist:
            return render(request,'experiment/error.html',{"message":"no crowd assignment"}) 
	
	#link user to profile
   	up1 = UserProfile.objects.filter(user=request.user,crowd=cm.crowd).first()
	if up1:
		pro_hint_list = ProfileHint.objects.filter(person_id=up1.profile.person_id,version_id=cm.crowd.version_id, crowd_size = cm.crowd.size)
		

	else:
		pro_id = Profile.objects.raw('SELECT * FROM experiment_profile WHERE version_id=%s AND crowd_size=%s AND id NOT IN (SELECT profile_id FROM experiment_userprofile WHERE profile_id IS NOT NULL AND crowd_id = %s) ORDER BY id LIMIT 1',[cm.crowd.version_id,cm.crowd.size, cm.crowd.id])[0]
        	log.debug(pro_id.id)
		log.debug(cm.crowd.version_id)
		log.debug(cm.crowd.size)
		log.debug(cm.crowd.id)
        	pro = Profile.objects.get(id=pro_id.id)
		#return render(request,'experiment/error.html',{"message":pro_id)})
		up = UserProfile.objects.create(user=request.user,profile=pro_id, crowd = cm.crowd)
        
		pro_hint_list = ProfileHint.objects.filter(person_id=pro.person_id,version_id=cm.crowd.version_id, crowd_size = cm.crowd.size)
	#list_hintId =ProfileHint.objects.get(profile_id=up.profile_id, version_id=cm.crowd.version_id, crowd_size = cm.crowd.size)
	hint_list1 = []
	for hint in pro_hint_list:
		log.debug(hint.hint_id)
		hint_list1.append(ProblemHint.objects.get(id=hint.hint_id))
		

	hint_list = serializers.serialize( "python", hint_list1)
	log.debug("collection of obj")
	log.debug(hint_list)
	
        # We want to show the last 50 messages, ordered most-recent-last
        #statements = reversed(discussion.statements.order_by('-timestamp'))
        statements = Statement.objects.filter(discussion=discussion)
	          
	if cm.crowd.size == 30 :
		disp = "You're in a crowd of 30 people."
	elif cm.crowd.size == 3:
		disp = "You're in a group of 3 people."
	else:
		disp = "You're in a group of Unknown size."
         
        return render(request, "forum/discussion.html", {
       
	'discussion': discussion,
        'statements': statements,
        'hints':hint_list,	
	'disp': disp
        })
    else:
        return redirect('experiment.views.home_page')
