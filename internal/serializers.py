from django.contrib.auth.models import User, Group
from rest_framework import serializers
from internal.models import Link, Event

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ("id", "url", "creator")

class EventSerializer(serializers.ModelSerializer):
    link = LinkSerializer(read_only=True)
    class Meta:
        model = Event
        fields = ("id", "link", "time")
