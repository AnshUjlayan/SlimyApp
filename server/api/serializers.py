from rest_framework import serializers
from .models import User, Playlist, PlaylistInteraction, Video, VideoOrder, Comment, CommentInteraction
from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'name', 'password')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'


class PlaylistInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistInteraction
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VideoOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoOrder
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class CommentInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentInteraction
        fields = '__all__'
