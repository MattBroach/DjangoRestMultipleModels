from django.db import models


class Play(models.Model):
    genre = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    year = models.IntegerField()


class Poem(models.Model):
    title = models.CharField(max_length=200)
    style = models.CharField(max_length=100)
