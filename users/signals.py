from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from PIL import Image
from users.models import Profile

def updateUser(sender, instance, **kwargs):
    user = instance
    if user.email != '':
        user.username = user.email

pre_save.connect(updateUser, sender=User)

def image_compressor(sender, **kwargs):
    if kwargs["created"]:
        with Image.open(kwargs["instance"].image_url.path) as photo:
            photo.save(kwargs['instance'].image_url.path, optimize=True, quality=50)

post_save.connect(image_compressor, sender=Profile)