from rest_framework import serializers

from .models import Play, Poem


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ('genre', 'title', 'year')


class PoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poem
        fields = ('title', 'style')
