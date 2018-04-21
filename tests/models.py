from django.db import models


class Play(models.Model):
    genre = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    author = models.ForeignKey('tests.Author', related_name='plays', on_delete=models.CASCADE)


class Poem(models.Model):
    title = models.CharField(max_length=200)
    style = models.CharField(max_length=100)
    author = models.ForeignKey('tests.Author', related_name='poems', on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=100)
