from django.db import models
from django.contrib.auth.models import User

# Create your models here.

def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=80, blank=False, null=False)
    interests = models.CharField(max_length=80, blank=False, null=False)
    image_url = models.ImageField(upload_to=upload_to, blank=True, null=True, default='avatar.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

