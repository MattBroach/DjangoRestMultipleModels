from rest_framework import serializers

from .models import Author, Play, Poem


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('name',)


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ('genre', 'title', 'year')


class PoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poem
        fields = ('title', 'style')


class PlayWithAuthorSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Play
        fields = ('genre', 'title', 'year', 'author')


class PoemWithAuthorSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Poem
        fields = ('title', 'style', 'author')


class AuthorListSerializer(AuthorSerializer):
    plays = PlaySerializer(many=True)
    poems = PoemSerializer(many=True)

    class Meta:
        model = Author
        fields = AuthorSerializer.Meta.fields + ('plays', 'poems')
