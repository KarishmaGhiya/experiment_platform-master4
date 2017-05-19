from django.shortcuts import render, redirect
from django.http import HttpResponse
from waiting_room import views
import logging
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ExpUser,Crowd_Members, Crowd, Consent_form, Questions
from random import randint

log = logging.getLogger(__name__)


def home_page(request):
    if not request.user.is_authenticated():
        workerid = request.GET.get('workerId')
	hitid = request.GET.get('hitId')
        if not workerid or workerid=='':
            ### no worker id set
            return render(request,'experiment/error.html',{"message":"no worker id"})
	elif not hitid or hitid=='':
	    return render(request,'experiment/error.html',{"message":"no hit id"})
        else:
            ### create user
            user, new = User.objects.get_or_create(username=workerid,first_name=hitid)
            user.set_password("mypass")
            user.save()
            user = authenticate(username=workerid,password="mypass")
            if user:
                login(request,user)
		return redirect("experiment.views.home_page")
            else:
                return render(request,'waiting_room/error.html',{"message":"could not authenticate"})
            
            if new:
                messages.warning(request,"Fill in Nickname")
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
        messages.warning(request,"Fill in Nickname")
        return render(request,'experiment/nickname.html') 
    
    return render(request,'experiment/error.html',{"message":"problem in authenticated"}) 
        
def nickname(request):
    
    if request.user.is_authenticated():
        if request.method == "POST":
            nickname = request.POST.get('nickname')	    
            myuser = request.user
	    s = randint(1,100000)	    
            userexp = ExpUser.objects.create(user=myuser,nickname=nickname,expstage="wait_room",secret_code = s)	    
	    consent_user = Consent_form.objects.create(user=myuser,agree='signed')

            return redirect('experiment.views.before_task')

        return render(request,'experiment/nickname.html')
    else:
        return redirect('experiment.views.home_page')

def finish(request):
    if request.user.is_authenticated(): 
	u = ExpUser.objects.get(user=request.user)
	s = u.secret_code
        return render(request,'experiment/finish.html',{"secret_code":s})
    else:
        return redirect('experiment.views.home_page')


'''def consent(request):
	workerid = request.GET.get('workerId')
        if not workerid or workerid=='':
            ### no worker id set
            return render(request,'experiment/error.html',{"message":"no worker id"})
	return render(request,'experiment/consent.html')'''

def survey(request):
    if request.user.is_authenticated(): 
        u = ExpUser.objects.get(user=request.user)
        u.expstage = "survey"
        u.save()
	if request.method == "POST":
		GrpSol = request.POST.get('group_soln')
		InvSol = request.POST.get('inv_sol')
		
		DegConf = int(request.POST.get('deg_conf'))
		Diff = request.POST.get('difference')
		GrpExp1_1 = int(request.POST.get('deg_agree1'))
		GrpExp1_2 = int(request.POST.get('deg_agree2'))
		GrpExp1_3 = int(request.POST.get('deg_agree3'))
		GrpExp1_4 = int(request.POST.get('deg_agree4'))
		GrpExp1_5 = int(request.POST.get('deg_agree5'))
		GrpExp1_6 = int(request.POST.get('deg_agree6'))
		GrpExp1_7 = int(request.POST.get('deg_agree7'))
		GrpExp2 = request.POST.get('group_exp2')
		Sex = request.POST.get('gender')
		Age = int(request.POST.get('age'))
		Edu = request.POST.get('edu')
		Empl_var = request.POST.getlist('empl[]')
		i = 0
		Empl_schoolFull = 'no'
		Empl_schoolPart = 'no'
		Empl_part = 'no'
		Empl_full = 'no'
		for i in range(0,len(Empl_var)):
			if Empl_var[i] == "school_full":
				Empl_schoolFull = 'yes'
			if Empl_var[i] == "school_part":
				Empl_schoolPart = 'yes'
			if Empl_var[i] == "part_time":
				Empl_part = 'yes'
			if Empl_var[i] == "full_time":
				Empl_full = 'yes' 
		
		Country = request.POST.get('country')
		HITs = request.POST.get('HITs')
		myuser = request.user
		question_user = Questions.objects.create(worker=myuser,GrpSol=GrpSol, InvSol=InvSol,  DegConf=DegConf, Diff=Diff,GrpExp1_1=GrpExp1_1,GrpExp1_2=GrpExp1_2, GrpExp1_3=GrpExp1_3,GrpExp1_4=GrpExp1_4,GrpExp1_5=GrpExp1_5,GrpExp1_6=GrpExp1_6,GrpExp1_7=GrpExp1_7,GrpExp2=GrpExp2, Sex=Sex,Age=Age, Edu=Edu,Empl_schoolFull=Empl_schoolFull,Empl_schoolPart =Empl_schoolPart,Empl_part =Empl_part,Empl_full=Empl_full,Country=Country,HITs=HITs )
		return redirect('experiment.views.finish')	


        return render(request,'experiment/survey.html')
    else:
        return redirect('experiment.views.home_page')

def wait_room(request):
    if request.user.is_authenticated(): 
        return render(request,'waiting_room/wait_home.html')
    else:
        return redirect('experiment.views.home_page')
   
def before_task(request):
    if request.user.is_authenticated(): 
		if request.method == "POST":
			#check crowd id of empty crowd
        		#which_crowd = Crowd.objects.Crowd_which_assign()
			
   			which_crowd = Crowd.objects.Crowd_which_assign()
		        log.debug("which_crowd=%d",which_crowd)
        		crowd =  Crowd.objects.get(id = which_crowd)     		
			count_existing = Crowd_Members.objects.filter(crowd=crowd).count()
			member_num = count_existing
			cohortid = (count_existing)/3
	        	crowd.members.create(user=request.user,crowd=crowd,cohort_id=cohortid,member_num=member_num)
	        	eu = ExpUser.objects.get(user=request.user)
	        	eu.expstage = "task"
			eu.save()
		
			task_url=''
            		if crowd.communication == '_forum':
		            task_url='http://crowdps.umd.edu/forum/room'
		        elif crowd.communication == '_chat':
		            task_url='http://crowdps.umd.edu/chat/room'
        		task_url += str(which_crowd)
		
			return redirect(task_url)

      		return render(request,'experiment/wait_before_task.html')
    else:
        return redirect('experiment.views.home_page') 

def forumapp(request):

    return render(request,'forum/about.html')

def chatapp(request):
    return render(request,'chat/about.html')
    
def error_page(request):
    #rproblem = Problem.objects.random()
    version = 1
    cm = Crowd.objects.create(version_id=version,size=3,communication="_forum")
    m = "Problem"+str(version)
    return render(request,'experiment/error.html',{"message":m})


