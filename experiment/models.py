from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import logging
from django.db.models import Count
from random import randint, sample
from datetime import datetime, timedelta

log = logging.getLogger(__name__)
# Create your models here.

class Consent_form(models.Model):
    user = models.ForeignKey(User)
    agree = models.CharField(max_length=35,null=True, default=None,blank = True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

class ExpUser(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=35, null=True, default=None,
                                  blank=True)
    expstage = models.CharField(max_length=35, null=True, default=None,
                                 blank=True)
    secret_code = models.IntegerField(unique=True)    
    

    def __unicode__(self):
        return "<ExpUser:{}>".format(self.nickname)



'''class ProblemManager(models.Manager):

    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]'''




class ProblemHint(models.Model):
    hint_type = models.CharField(max_length=255)
    candidate_1 = models.CharField(max_length=255)
    candidate_2 = models.CharField(max_length=255)
    candidate_3 = models.CharField(max_length=255)
    candidate_4 = models.CharField(max_length=255)
            
 

       
class CrowdManager(models.Manager):

	def Crowd_which_assign(self):
		CHAT_COMMUNICATION = '_chat'
		FORUM_COMMUNICATION = '_forum'
		#Filter for date = today & creation time > an hour ago
		crowds = Crowd.objects.all()
		time_threshold = datetime.now() - timedelta(hours=1) ####UPDATE THE TIME WINDOW AFTER CREATION OF ROOM/FORUM
		crowds_recent = crowds.filter(creation_date__gt=time_threshold)
		
		
		which_crowd = 0
		#Check which crowd is not full,  and get that crowd id	
		cr = Crowd.objects.select_related().annotate(num_members=Count('members'))
		#print A[0].num_B	

		for (i,crowd) in enumerate(crowds_recent):	
			log.debug(crowd.size)
			log.debug(cr[i].num_members)
			if cr[i].num_members < crowd.size :
				which_crowd = crowd.id
				break

		#if all crowds are full, crowd id = 0 , create a new crowd and get that crowd id
		if which_crowd == 0 :
			#write logic to assign chat/forum, size, task
			## choose size of crowd
			crowd_size = [3,30]
			rsize = sample(crowd_size,1)[0]
			###rsize = 3
			rcom = FORUM_COMMUNICATION
			if rsize==3:
			    rcom = sample([CHAT_COMMUNICATION,FORUM_COMMUNICATION],1)[0]
			####UPDATE THE VERSION FOR CROWD ASSIGNMENT EACH TIME YOU RUN EXP
			version = 8
			new_crowd = Crowd.objects.create(version_id=version,size=rsize,communication = rcom)
			
			which_crowd = new_crowd.id	
			

		return which_crowd

	def Crowd_assign(self):
		CHAT_COMMUNICATION = '_chat'
		FORUM_COMMUNICATION = '_forum'
		#Filter for date = today & creation time > two hour ago
		crowds = Crowd.objects.all()
		time_threshold = datetime.now() - timedelta(hours=2)
		crowds_recent = crowds.filter(creation_date__gt=time_threshold)
		
		
		which_crowd = 0
		#Check which crowd is not full,  and get that crowd id	
		cr = Crowd.objects.select_related().annotate(num_members=Count('members'))
		#print A[0].num_B	

		for (i,crowd) in enumerate(crowds_recent):	
			log.debug(crowd.size)
			log.debug(cr[i].num_members)
			if cr[i].num_members < crowd.size and crowd.size == 30 :
				which_crowd = crowd.id
				break

		#if all crowds are full, crowd id = 0 , create a new crowd and get that crowd id
		

		return which_crowd



class Crowd(models.Model):
	#crowd-id: automatically added 
   
    version_id = models.PositiveIntegerField()
    GROUP_SIZE = 3
    CROWD_SIZE = 30
    SIZE_CHOICES = (
	    (GROUP_SIZE, '_group'),
	    (CROWD_SIZE, '_crowd'), 
        )
	#size of 3 or 30
    size = models.PositiveIntegerField(choices = SIZE_CHOICES, default=GROUP_SIZE)
    CHAT_COMMUNICATION = '_chat'
    FORUM_COMMUNICATION = '_forum'
    COMMUNICATION_CHOICES = (
		(CHAT_COMMUNICATION, '_chat'),
		(FORUM_COMMUNICATION, '_forum'),
	)
	#COMMUNICATION CONDITION via chat or forum
    communication = models.CharField(choices = COMMUNICATION_CHOICES, default = CHAT_COMMUNICATION ,max_length=255)
    
    creation_date = models.DateTimeField(default=timezone.now, db_index=True)
    is_active = models.IntegerField(default=1)
	#@property
    objects = CrowdManager()
	

class Crowd_Members(models.Model):
    crowd = models.ForeignKey(Crowd, on_delete = models.CASCADE, related_name = 'members')
    user = models.OneToOneField(User)
    time_joined = models.DateTimeField(default=timezone.now)
    cohort_id = models.PositiveIntegerField()
    member_num = models.IntegerField(default=None)


'''class UserHints(models.Model):
    user = models.ForeignKey(User)
    crowd = models.ForeignKey(Crowd)
    problem = models.ForeignKey(Problem)
    hint = models.ForeignKey(ProblemHint)'''

class Questions(models.Model):
    worker = models.OneToOneField(User, primary_key = True)
    GrpSol = models.TextField()  
    InvSol = models.TextField()
    
    DegConf = models.IntegerField()
    Diff = models.TextField()
    GrpExp1_1 = models.PositiveIntegerField()
    GrpExp1_2 = models.PositiveIntegerField()
    GrpExp1_3 = models.PositiveIntegerField()
    GrpExp1_4 = models.PositiveIntegerField()
    GrpExp1_5 = models.PositiveIntegerField()
    GrpExp1_6 = models.PositiveIntegerField()
    GrpExp1_7 = models.PositiveIntegerField()
    GrpExp2 = models.TextField()
    MALE = 'male'
    FEMALE = 'female'
    GENDER_CHOICES = (
		(MALE,'male'),
		(FEMALE,'female'),
       )
    Sex = models.CharField(max_length = 35,choices = GENDER_CHOICES, default = MALE)
    Age = models.PositiveIntegerField()
    LESS_6 = 'less than 6'
    LESS_12 = 'less than 12'
    HIGH = 'high school'
    SOME = 'some college'
    UNDERGRAD = 'undergrad'
    MASTERS = 'masters'
    DOCTORAL = 'doctoral'

    EDUCATION_CHOICES = (
	(LESS_6,'less than 6'),
	(LESS_12,'less than 12'),
	(HIGH, 'high school'),
	(SOME, 'some college'),
	(UNDERGRAD,'undergrad'),
	(MASTERS,'masters'),
	(DOCTORAL,'doctoral'),
    )


    Edu = models.CharField(max_length = 35, choices = EDUCATION_CHOICES, default = LESS_6)
    YES ='yes'
    NO = 'no'

    EMPL_CHOICES= (
		(YES,'yes'),
		(NO,'no'),
	)
    Empl_schoolFull = models.CharField(max_length = 35, choices = EMPL_CHOICES, default=NO)
    Empl_schoolPart =  models.CharField(max_length = 35, choices = EMPL_CHOICES, default=NO)
    Empl_full =  models.CharField(max_length = 35, choices = EMPL_CHOICES, default=NO)
    Empl_part =  models.CharField(max_length = 35, choices = EMPL_CHOICES, default=NO)
    Country = models.TextField()
    HITs = models.TextField()

class TaskUser(models.Model):
    user = models.ForeignKey(User)
    crowd = models.SlugField(max_length=35)
    time_type= models.CharField(max_length=35)
    time_stamp = models.DateTimeField(default=timezone.now, db_index=True)
    
  

class Profile(models.Model):
        person_id = models.PositiveIntegerField()
	version_id = models.PositiveIntegerField()
	GROUP_SIZE = 3
    	CROWD_SIZE = 30
    	SIZE_CHOICES = (
	    (GROUP_SIZE, '_group'),
	    (CROWD_SIZE, '_crowd'), 
          )
	#size of 3 or 30
	crowd_size = models.PositiveIntegerField(choices = SIZE_CHOICES, default=GROUP_SIZE)
	
class ProfileHint(models.Model):
    person_id = models.PositiveIntegerField()
    version_id = models.PositiveIntegerField()    
    hint = models.ForeignKey(ProblemHint)
    GROUP_SIZE = 3
    CROWD_SIZE = 30
    SIZE_CHOICES = (
	    (GROUP_SIZE, '_group'),
	    (CROWD_SIZE, '_crowd'), 
          )
    #size of 3 or 30
    crowd_size = models.PositiveIntegerField(choices = SIZE_CHOICES, default=GROUP_SIZE)

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    profile = models.ForeignKey(Profile)
    crowd = models.ForeignKey(Crowd)




