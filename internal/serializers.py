from django.contrib.auth.models import User, Group
from rest_framework import serializers
from internal.models import Link, Event, Preference

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ("id", "url", "creator")

class EventSerializer(serializers.ModelSerializer):
    link = LinkSerializer(read_only=True)
    class Meta:
        model = Event
        fields = ("id", "link", "time")

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ('id', 'background_img', 'profile_img', 'media_prefix')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
