from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import logging
from django.db.models import Count
from random import randint, sample


log = logging.getLogger(__name__)
# Create your models here.


class ExpUser(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=35, null=True, default=None,
                                  blank=True)
    expstage = models.CharField(max_length=35, null=True, default=None,
                                 blank=True)


    def __unicode__(self):
        return "<ExpUser:{}>".format(self.nickname)


class ProblemManager(models.Manager):

    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Problem(models.Model):
    prob_num = models.IntegerField()
    instructions = models.TextField()
    
	#@property
    objects = ProblemManager()

class ProblemHintManager(models.Manager):

    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_ints = sample(range(0,count),6)
        random_sample = [obs for (i,obs) in enumerate(self.all()) if i in random_ints] 
        return random_sample

class ProblemHint(models.Model):
    problem = models.ForeignKey(Problem, related_name = 'hints')
    hint_num = models.IntegerField()
    hint_type = models.CharField(max_length=255)
    hint_text = models.TextField()
    
    objects = ProblemHintManager()        
        
class CrowdManager(models.Manager):

	def Crowd_which_assign(self):
		CHAT_COMMUNICATION = '_chat'
		FORUM_COMMUNICATION = '_forum'
		crowds = Crowd.objects.all()
		which_crowd = 0
		#Check which crowd is not full,  and get that crowd id	
		cr = Crowd.objects.select_related().annotate(num_members=Count('members'))
		#print A[0].num_B	

		for (i,crowd) in enumerate(crowds):	
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
			rcom = FORUM_COMMUNICATION
			if rsize==3:
			    rcom = sample([CHAT_COMMUNICATION,FORUM_COMMUNICATION],1)[0]

			rproblem = Problem.objects.random()
			
			new_crowd = Crowd.objects.create(Problem=rproblem,size=rsize,communication = rcom)
			which_crowd = new_crowd.id	


		return which_crowd



class Crowd(models.Model):
	#crowd-id: automatically added 
    Problem = models.ForeignKey(Problem)

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

	#@property
    objects = CrowdManager()
	

class Crowd_Members(models.Model):
    crowd = models.ForeignKey(Crowd, on_delete = models.CASCADE, related_name = 'members')
    user = models.ForeignKey(User)
    time_joined = models.DateTimeField(default=timezone.now)
    cohort_id = models.PositiveIntegerField()



class UserHints(models.Model):
    user = models.ForeignKey(User)
    crowd = models.ForeignKey(Crowd)
    problem = models.ForeignKey(Problem)
    hint = models.ForeignKey(ProblemHint)

