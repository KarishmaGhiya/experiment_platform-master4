from django.shortcuts import render, redirect
from django.http import HttpResponse
from waiting_room import views
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ExpUser,Crowd_Members, Crowd, Problem, Consent_form
from random import randint



def home_page(request):

    if not request.user.is_authenticated():
        workerid = request.GET.get('workerId')
        if not workerid or workerid=='':
            ### no worker id set
            return render(request,'experiment/error.html',{"message":"no worker id"})
        else:
            ### create user
            user, new = User.objects.get_or_create(username=workerid)
            user.set_password("mypass")
            user.save()
            user = authenticate(username=workerid,password="mypass")
            if user:
                login(request,user)
            else:
                return render(request,'waiting_room/error.html',{"message":"could not authenticate"})
            
            if new:
                messages.warning(request,"Fill in Consent Form & Nickname")
                return render(request,'experiment/nickname.html') 
		#return render(request,'experiment/consent.html')
        return render(request,'experiment/error.html',{"message":"problem in not authenticated"}) 
                
            
    myuser = request.user
    try:
        u = ExpUser.objects.get(user=myuser)
        if u.expstage in ["nickname","wait_room","survey"]: 
            return redirect("experiment.views."+u.expstage)  
        elif u.expstage=="task":
            try:
                cm = Crowd_Members.objects.get(user=myuser)
                url = ''
                if cm.crowd.communication == '_forum':
                    url ='http://crowdps.umd.edu/forum/room'+str(cm.crowd.id)
                elif cm.crowd.communication == '_chat':
                    url ='http://crowdps.umd.edu/chat/room'+str(cm.crowd.id)
                else:
                    return render(request,'experiment/error.html',{"message":"on task bad crowd.communication"}) 

                #redirect('http://127.0.0.1:8000/chat/room4')
                return redirect(url)

            #except Crowd_Members.DoesNotExist:  
            except:  
                return render(request,'experiment/error.html',{"message":"on task no crowd"})
            return render(request,'experiment/error.html',{"message":"problem in task"})          
        else:
            return render(request,'experiment/nickname.html')
    except ExpUser.DoesNotExist:
        messages.warning(request,"Fill in Consent Form & Nickname")
        return render(request,'experiment/nickname.html') 
    
    return render(request,'experiment/error.html',{"message":"problem in authenticated"}) 
        
def nickname(request):

    if request.user.is_authenticated():
        if request.method == "POST":
            nickname = request.POST.get('nickname')
            myuser = request.user
            userexp = ExpUser.objects.create(user=myuser,nickname=nickname,expstage="wait_room")
            #return render(request,'waiting_room/wait_home.html')#redirect to views
	    consent_user = Consent_form.objects.create(user=myuser,agree='signed')
	    return redirect('experiment.views.wait_room')
        return render(request,'experiment/nickname.html')
    else:
        return redirect('experiment.views.home_page')

def finish(request):
    if request.user.is_authenticated(): 
        return render(request,'experiment/finish.html')
    else:
        return redirect('experiment.views.home_page')


def consent(request):
	if request.user.is_authenticated():
	    if request.method== "POST":
		if request.POST.get('check',True) :
			workerid = request.GET.get('workerId')
			consent_user = Consent_form.objects.create(user=workerid,agree='signed')
			#url_generated = 
			return render(request,'experiment/nickname.html')
		else:
			return render(request,'experiment/error.html',{"message":"You have to agree to the conditions to participate. PLease tick the checkbox"})
            return render(request,'experiment/nickname.html')
        else:
	    return redirect('experiment.views.home_page')		
		

	

def survey(request):
    if request.user.is_authenticated(): 
        u = ExpUser.objects.get(user=request.user)
        u.stage = "survey"
        u.save()
        return render(request,'experiment/survey.html')
    else:
        return redirect('experiment.views.home_page')

def wait_room(request):
    if request.user.is_authenticated(): 
        return render(request,'waiting_room/wait_home.html')
    else:
        return redirect('experiment.views.home_page')
    

def forumapp(request):

    return render(request,'forum/about.html')

def chatapp(request):
    return render(request,'chat/about.html')
    
def error_page(request):
    rproblem = Problem.objects.random()
    cm = Crowd.objects.create(Problem=rproblem,size=3,communication="_forum")
    m = "Problem"+str(rproblem.id)
    return render(request,'experiment/error.html',{"message":m})


