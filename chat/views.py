import random
import string
from django.db import transaction
from django.shortcuts import render, redirect
import haikunator
from .models import Room
from experiment.models import Crowd_Members, Crowd, Problem, ProblemHint, ProfileHint,UserProfile, Profile, Documents

def about(request):
    return render(request, "chat/about.html")

def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room = None
    while not new_room:
        with transaction.atomic():
            h = haikunator.Haikunator()
            label = h.haikunate()
            #label = haikunator.haikunate()
            if Room.objects.filter(label=label).exists():
                continue
            new_room = Room.objects.create(label=label)
    return redirect(chat_room, label=label)

def chat_room(request, label):
    """
    Room view - show the room, with latest messages.

    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    if request.user.is_authenticated(): 
        # If the room with the given label doesn't exist, automatically create it
        # upon first visit (a la etherpad).
        room, created = Room.objects.get_or_create(label=label)
        
        # get problem 
        try:
            cm = Crowd_Members.objects.get(user=request.user)
        except Crowd_Members.DoesNotExist:
            return render(request,'experiment/error.html',{"message":"no crowd assignment"}) 

	#link user to profile
	pro_id = Profile.objects.raw('SELECT * FROM experiment_profile WHERE problem=%s AND crowd_size=%s AND id NOT IN (SELECT profile_id FROM experiment_userprofile WHERE profile_id IS NOT NULL)',[cm.crowd.Problem,cm.crowd.size])
	up = UserProfile.objects.create(user_id=request.user,profile_id=pro_id)
	list_hintId =ProfileHint.objects.get(profile_id=up.profile_id)
	uhints = []
	for h in list_hintId:
		uhints.append(h.hint.hint_text)
        '''
        # create or get userhint
        uhints = UserHints.objects.filter(user=request.user)
        if len(uhints)==0:
            hints = ProblemHint.objects.random(cm.cohort_id,cm.crowd.Problem.id)
            uhints = []
            for h in hints:
                uh = UserHints.objects.create(user=request.user,crowd=cm.crowd,problem=cm.crowd.Problem,hint=h)
                uhints.append(uh)
        uhints = [uh.hint.hint_text for uh in uhints]
	'''        
	# We want to show the last 50 messages, ordered most-recent-last
        messages = reversed(room.messages.order_by('-timestamp')[:50])
	try:
            cm_document = Documents.objects.get(id=cm.crowd.doc.id)
	    if cm.crowd.size == 30 :
		disp = "You're in a crowd of 30 people"
	    elif cm.crowd.size == 3:
		disp = "You're in a group of 3 people"
	    else:
		disp = "unknown size"
        except Documents.DoesNotExist:
            return render(request,'experiment/error.html',{"message":"no document"}) 
        return render(request, "chat/room.html", {
            'room': room,
            'messages': messages,
            'problem':cm.crowd.Problem.instructions,
            'hints':uhints,
	    'url':cm_document.document_url,
	    'disp': disp
        })
    else:
        return redirect('experiment.views.home_page')
    """
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "chat/room1.html", {
        'room': room,
        'messages': messages,
    })"""
