from django.db import models
from django.contrib.auth.models import User

from django.urls import reverse

class Profile(models.Model):
    class Meta:
        app_label = 'user'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    bio = models.TextField(max_length=200, blank=True)

    phone = models.CharField(max_length=20, help_text='Enter phone number.')
    address = models.CharField(max_length=100, help_text='Enter address.')

    available = models.BooleanField(default=False)

    def email(self):
        return self.user.username
        
    def __str__(self):
        return self.user.username