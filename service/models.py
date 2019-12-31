from django.db import models
from django.urls import reverse  # To generate URLS by reversing URL patterns

from django.conf import settings

# Create your models here.

class ServicePostComment(models.Model):
    class Meta:
        app_label = "service"
 
    # comment text
    text = models.CharField(max_length=800, blank=False)
    
    # A comment can have only one owner, but a owner can have many comments
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    created_datetime = models.DateTimeField(blank=False)

    # A comment can belong to only one service post
    post = models.ForeignKey('ServicePost', on_delete=models.CASCADE, null=True)

    # If private, only the creator & corresponding post owner can see the comment and not other users
    is_private = models.BooleanField(default=False)


# Each service post corresponds to a (virtual) service offered, plus post info
# This model links to the service and defines information related to the post
class ServicePost(models.Model):
    class Meta:
        app_label = "service"

    """Service model"""
    # skipping id:primary_key definition to allow Django to auto create and auto-increment id
    
    # title of the post, not service it belongs to
    title = models.CharField(max_length=80, blank=False, help_text='Enter service title.')

    # description of the post
    description = models.CharField(max_length=1024, blank=False, help_text='Enter description for the service.')

    # Each service post instance is of type request/offering.
    is_request_post = models.BooleanField(default=True)

    # Link the user to whom this post instance belongs to; a post is owned by only one user
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # when the record was created, modified, and closed.
    created_datetime = models.DateTimeField(editable=False)
    modified_datetime = models.DateTimeField(blank=True, null=True)
    closed_datetime = models.DateTimeField(blank=True, null=True)
    ''' USAGE in views.py:
    from django.utils import timezone
    created_d = timezone.now()
    '''
    # the service this post refers to
    service = models.OneToOneField('Service', on_delete=models.SET_NULL, null=True)

    def get_absolute_url(self):
        """Returns the url to access a detail record for this post."""
        return reverse('service:detail', args=[str(self.id)])


# Each service post corresponds to an actual service
class Service(models.Model):
    class Meta:
        app_label = 'service'

    # name of the actual service, not its post
    name = models.CharField(max_length=120, blank="False")

    # info related to the service
    info = models.CharField(max_length=300, blank=True)

    # when the service starts from and ends
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)

    # Location of the service
    location = models.CharField(max_length=50, blank=True)

    # A service can contain many tags; a tag can be used in many services.
    tags = models.ManyToManyField('Tag', help_text='Choose a tag.')

    def get_tags(self):
        return ", ".join([p.label for p in self.tags.all()])



class Tag(models.Model):
    class Meta:
        app_label = 'service'
        
    # skipping id:primary_key definition to allow Django to auto create and auto-increment id
    label = models.CharField(unique=True, max_length=60, blank=False, help_text='Enter tag label.')
    
    def __str__(self):
        """String for representing the Model object."""
        return self.label


class Notification(models.Model):
    class Meta:
        app_label = "service"
 
    # notification text
    text = models.CharField(max_length=800, blank=False)
    
    # A Notification can have only one owner, but a owner can have many notifications
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    created_datetime = models.DateTimeField(blank=False)

    is_read = models.BooleanField(default=False)

    target_url = models.CharField(max_length=800, blank=False) 
