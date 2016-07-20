from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from model_utils import ContentTypeAware, MttpContentTypeAware
from django.contrib.auth.models import User

class Discussion(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)

    def __unicode__(self):
        return self.label

class Statement(MttpContentTypeAware):
    discussion = models.ForeignKey(Discussion, related_name='statements')
    user = models.ForeignKey(User)
    handle = models.TextField()
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    isreply = models.IntegerField(default=0)
    parent = TreeForeignKey('self',related_name='children',null=True,blank=True,db_index=True)
    parentid = models.IntegerField(default=0)
    ups = models.IntegerField(default=0)
    downs = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
#    level = models.IntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['timestamp']
       
#    def create(cls,handle,message,parent,isreply,parentid):
#    
#        statement = cls(handle=handle,
#                        message=message,
#                        isreply=isreply,
#                        parentid=parentid)
                        
#        if isinstance(parent,Discussion):
#            discussion = parent
#            statement.discussion = discussion
#        if isinstance(parent,Comment):
#            discussion = parent.discussion
#            statement.discussion = discussion
#            statement.parent = parent
#        else:
#            return
#        return statement
                        

    def __unicode__(self):
        return '[{timestamp}] {handle}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p UTC')
    
    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': self.formatted_timestamp, 'id': self.id,'isreply': self.isreply, 'parentid': self.parentid, 'score':self.score}

    def update_score(self):
        return {'id':self.id,'score':self.score}

class Vote(models.Model):
    user = models.ForeignKey(User)
    handle = models.TextField()
    statement = models.ForeignKey(Statement, related_name='votes')
    value = models.IntegerField(default=0)


    def new_vote(self):

                    
        #statement2 = Statement.objects.get(id=data['id'])
        self.statement.score += self.value

        if self.value == 1:
            self.statement.ups += 1
        elif self.value == -1:
            self.statement.downs += 1

        self.statement.save()
        #return vote
    

    def change_vote(self, new_vote_value):
        if self.value == -1 and new_vote_value == 1:  # down to up
            vote_diff = 2
            self.Statement.score += 2
            self.Statement.ups += 1
            self.Statement.downs -= 1
        elif self.value == 1 and new_vote_value == -1:  # up to down
            vote_diff = -2
            self.Statement.score -= 2
            self.Statement.ups -= 1
            self.Statement.downs += 1
        elif self.value == 0 and new_vote_value == 1:  # canceled vote to up
            vote_diff = 1
            self.Statement.ups += 1
            self.Statement.score += 1
        elif self.value == 0 and new_vote_value == -1:  # canceled vote to down
            vote_diff = -1
            self.Statement.downs += 1
            self.Statement.score -= 1
        else:
            return None

        self.value = new_vote_value
        self.Statement.save()
        self.save()

        return vote_diff

    def cancel_vote(self):
        if self.value == 1:
            vote_diff = -1
            self.Statement.ups -= 1
            self.Statement.score -= 1
        elif self.value == -1:
            vote_diff = 1
            self.Statement.downs -= 1
            self.Statement.score += 1
        else:
            return None


        self.value = 0
        self.save()
        self.Statement.save()
        return vote_diff    
