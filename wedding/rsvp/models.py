from django.contrib.auth.models import User
from django.db import models
from tools.decorators import cached_property


class Invitation(models.Model):
    """A single invitation sent to a family at a given address."""
    
    user = models.ForeignKey(User, null=True, blank=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    rehearsal_dinner = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        """Return the formal name used to address this invitation."""

        # if there is only one adult, use the adult's formal name
        if len(self.adults) == 1:
            return unicode(self.adults[0])
            
        # okay, there are two adults -- if their last names match,
        # then we want a single, unified format
        # (e.g. "Mr. & Mrs. Jonathan Chappell")
        if self.adults[0].last_name == self.adults[1].last_name:
            return u'%(male_title)s & %(female_title)s %(male_first_name)s %(last_name)s' % {
                'female_title': self.adults[1].title,
                'last_name': self.adults[0].last_name,
                'male_title': self.adults[0].title,
                'male_first_name': self.adults[0].first_name,
            }
            
        # okay, the last names don't match; print the names out separately
        # and in their entirety
        # (e.g. "Mr. Daniel Beltz and Ms. Jessica Dymer")
        return u'%s & %s' % (self.adults[0], self.adults[1])
    
    @cached_property
    def adults(self):
        return self.invitee_set.filter(age_group='adult').order_by('-sex')
        
    @cached_property
    def children(self):
        return self.invitee_set.filter(age_group='children')
        
    @cached_property
    def infants(self):
        return self.invitee_set.filter(age_group='infants')
        
    
class Invitee(models.Model):
    """A specific person invited included on an invitation."""
    
    title = models.CharField(max_length=16)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    age_group = models.CharField(max_length=6, choices=(
        ('adult', 'Adult'),
        ('child', 'Child (2 - 16 years)'),
        ('infant', 'Infant (0 - 23 months)'),
    ), default='adult', db_index=True)
    sex = models.CharField(max_length=6, choices=(
        ('male', 'Male'),
        ('female', 'Female'),
    ), db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return '%s %s %s' % (self.title, self.first_name, self.last_name)
    

class RSVP(models.Model):
    """A response from an individual on whether they will attend,
    and their food order."""
    
    invitee = models.OneToOneField(Invitee, related_name='rsvp')
    accepts = models.BooleanField(default=True)
    food = models.CharField(max_length=16, choices=(
        ('chicken', 'Chicken'),
        ('fish', 'Fish'),
        ('steak', 'Steak'),
        ('vegetarian', 'Vegetarian'),
        ('gluten-free', 'Gluten Free'),
    ), null=True, blank=True)
    medium = models.CharField(max_length=10, choices=(
        ('mail', 'Mail'),
        ('online', 'Online'),
    ), help_text='The response medium this person used.', default='mail')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'RSVP: %s' % self.invitee
    

class Gift(models.Model):
    """A mapping between an invitation and the gift we received from
    the invitees. For thank you notes."""
    
    invitation = models.ForeignKey(Invitation)
    label = models.CharField(max_length=250, help_text='A terse statement of "what this gift is". For instance, "linen sheets", "gaming table".')
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.label