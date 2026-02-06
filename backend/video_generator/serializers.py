from rest_framework import serializers
from .models import VideoJob


class VideoJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoJob
        fields = "__all__"
