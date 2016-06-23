import random
import string
from django.db import transaction
from django.shortcuts import render, redirect
import haikunator
from .models import Discussion, Statement
from experiment.models import Crowd_Members, Crowd, Problem, ProblemHint, UserHints

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

        # create or get userhint
        # create or get userhint
        uhints = UserHints.objects.filter(user=request.user)
        if len(uhints)==0:
            hints = ProblemHint.objects.random()
            uhints = []
            for h in hints:
                uh = UserHints.objects.create(user=request.user,crowd=cm.crowd,problem=cm.crowd.Problem,hint=h)
                uhints.append(uh)
        uhints = [uh.hint.hint_text for uh in uhints]
        # We want to show the last 50 messages, ordered most-recent-last
        #statements = reversed(discussion.statements.order_by('-timestamp'))
        statements = Statement.objects.filter(discussion=discussion)

        return render(request, "forum/discussion.html", {
        'discussion': discussion,
        'statements': statements,
        'problem':cm.crowd.Problem.instructions,
        'hints':uhints
        })
    else:
        return redirect('experiment.views.home_page')
