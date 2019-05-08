from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils.timezone import now

# automatically generate token for every new user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True)

    def __str__(self):
        return self.user.username

# create Preferences object when User is created
@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        Preference.objects.create(user=instance)

# update preferences when User is updated
@receiver(post_save, sender=User)
def save_user_preference(sender, instance, **kwargs):
    instance.preference.save()

class Link(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return self.url

class Event(models.Model):
    
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    time = models.DateTimeField(default=now)

    def __str__(self):
        return '%s (%s)' % (self.link, self.time)
