from django.contrib.auth.models import User, Group
from rest_framework import serializers
from internal.models import Link, Preference

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = "__all__"

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ('id', 'background_img', 'profile_img', 'media_prefix')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
