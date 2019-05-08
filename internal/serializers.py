from django.contrib.auth.models import User, Group
from rest_framework import serializers
from internal.models import Link

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")

class LinkSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Link
        fields = ("id", "url", "creator")

