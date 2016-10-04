from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import logging
from django.db.models import Count
from random import randint, sample


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

    def random(self, cohort, task):
        
	#cohort how???? assignment of cohort in consumers.py? 
	#all_unique = ProblemHint.objects.raw('SELECT h.* FROM (SELECT uh.hint_id FROM experiment_userhints AS uh JOIN experiment_crowd_members AS cm ON uh.user_id=cm.user_id WHERE cohort_id=%s'[cohort]') AS u RIGHT JOIN experiment_problemhint AS h ON u.hint_id=h.id WHERE ISNULL(u.hint_id) AND h.problem_id=%s'[task]' AND h.hint_type="unique"')
	all_unique = ProblemHint.objects.raw('SELECT h.* FROM (SELECT uh.hint_id FROM experiment_userhints AS uh JOIN experiment_crowd_members AS cm ON uh.user_id=cm.user_id WHERE cohort_id=%s) AS u RIGHT JOIN experiment_problemhint AS h ON u.hint_id=h.id WHERE ISNULL(u.hint_id) AND h.problem_id=%s AND h.hint_type="unique"',[cohort, task])
        random_ints1 = sample(range(0,len(list(all_unique))),2)#is this correct???? should it be count of all_unique?
        random_sample1 = [obs for (i,obs) in enumerate(all_unique) if i in random_ints1] 

	all_shared = ProblemHint.objects.raw('SELECT h.* FROM (SELECT uh.hint_id,count(*) AS hintcount FROM experiment_userhints AS uh JOIN experiment_crowd_members AS cm ON uh.user_id=cm.user_id WHERE cohort_id=%s) AS u RIGHT JOIN experiment_problemhint AS h ON u.hint_id=h.id WHERE (ISNULL(u.hint_id) OR u.hintcount=1) AND h.problem_id=%s AND h.hint_type="shared"',[cohort, task])
	random_ints2 = sample(range(0,len(list(all_shared))),4)#is this correct???? should it be count of all_SHARED?
        random_sample2 = [obs for (i,obs) in enumerate(all_shared) if i in random_ints2] 
	random_sample = random_sample1 + random_sample2
	
        return random_sample

class ProblemHint(models.Model):
    problem = models.ForeignKey(Problem, related_name = 'hints')
    hint_num = models.IntegerField()
    hint_type = models.CharField(max_length=255)
    hint_text = models.TextField()
    
    objects = ProblemHintManager()        
 
class Documents(models.Model):
	document_url = models.TextField()
	problem_task = models.ForeignKey(Problem)
       
class CrowdManager(models.Manager):

	def Crowd_which_assign(self):
		CHAT_COMMUNICATION = '_chat'
		FORUM_COMMUNICATION = '_forum'
		crowds = Crowd.objects.all()
		which_crowd = 0
		#Check which crowd is not full,  and get that crowd id	
		cr = Crowd.objects.filter(is_active=1).select_related().annotate(num_members=Count('members'))
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
			#Documents.objects.raw('SELECT d.* FROM experiment_crowd as c right join experiment_crowd_docs as d on c.doc=d.id where isnull(c.crowd) and d.task=[insert task]')	
			all_docs =Documents.objects.raw('SELECT d.* FROM experiment_crowd AS c RIGHT JOIN experiment_documents AS d ON c.doc_id=d.id WHERE ISNULL(c.id) AND d.problem_task_id=%s',[rproblem.id]) 
			'''for d in all_docs:
				print("%s is the url for doc %s"% (d.document_url,d.id))'''
			#print("%s is %s." % (p.first_name, p.age))
			rdoc = all_docs[0]
			new_crowd = Crowd.objects.create(Problem=rproblem,size=rsize,communication = rcom, doc = rdoc)
			#new_crowd = Crowd.objects.create(Problem=rproblem,size=rsize,communication = rcom)
			which_crowd = new_crowd.id	
			#set google doc to crowd

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
    doc = models.OneToOneField(Documents, default=None,unique= True)
    is_active = models.IntegerField(default=1)
	#@property
    objects = CrowdManager()
	

class Crowd_Members(models.Model):
    crowd = models.ForeignKey(Crowd, on_delete = models.CASCADE, related_name = 'members')
    user = models.ForeignKey(User, unique = True)
    time_joined = models.DateTimeField(default=timezone.now)
    cohort_id = models.PositiveIntegerField()
    member_num = models.IntegerField(default=None)


class UserHints(models.Model):
    user = models.ForeignKey(User)
    crowd = models.ForeignKey(Crowd)
    problem = models.ForeignKey(Problem)
    hint = models.ForeignKey(ProblemHint)

class Questions(models.Model):
    worker = models.OneToOneField(User, primary_key = True)
    GrpSol = models.TextField()  
    InvSolWife = models.TextField()
    InvSolJob = models.TextField()
    InvSolCity = models.TextField()
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
    
  


