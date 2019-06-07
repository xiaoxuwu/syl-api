from django.contrib.auth.models import User, Group
from rest_framework import serializers
from internal.models import Link, Event, Preference

class LinkSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=False)

    class Meta:
        model = Link
        fields = ('id', 'url', 'creator', 'text', 'image', 'order', 'created', 'media_prefix')

class EventSerializer(serializers.ModelSerializer):
    link = LinkSerializer(read_only=True)
    class Meta:
        model = Event
        fields = ('id', 'link', 'date', 'time')

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ('id', 'background_img', 'profile_img', 'media_prefix')

class UserSerializer(serializers.ModelSerializer):
    ig_token = serializers.StringRelatedField()
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'ig_token')
