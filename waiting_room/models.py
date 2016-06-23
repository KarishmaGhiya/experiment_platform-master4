import json
from django.db import models
from django.utils.six import python_2_unicode_compatible 
from django.utils import timezone
from channels import Group
from django.contrib.auth.models import User

#from .settings import MSG_TYPE_MESSAGE





@python_2_unicode_compatible
class WaitRoom(models.Model):
    """
    A room for people to wait in to form groups of 3.
    """

    # Room title
    title = models.CharField(max_length=255)
    numwait = models.PositiveIntegerField(default=0)
    #message
    def __str__(self):
        return self.title

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("wait-room-%s" % self.id)

    def send_message(self, message, user, msg_type=0):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'wait-room': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
	    )
	def add_waiter(self):
	    self.numwait += 1
	    self.save()
	    
	def remove_waiter(self):
	    self.numwait = max(0,self.numwait-1)
	    self.save()
	

class WaitUser(models.Model):
    user = models.ForeignKey(User)
    wait_room = models.ForeignKey(WaitRoom, related_name='users')
    is_active = models.IntegerField(default=0)
    starttime = models.DateTimeField(default=timezone.now, db_index=True)
    endtime = models.DateTimeField(default=None, db_index=True,null=True)

    def __unicode__(self):
        return '[{timestamp}] : {message}'.format(**self.as_dict())

    def enter_wait(self):
        self.is_active = 1
        self.save()

    def leave_wait(self):
        self.is_active = 0
        self.endtime = timezone.now
        self.save()
    
    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')
    
    
    def as_dict(self):
        return { 'message': self.message, 'timestamp': self.formatted_timestamp}
