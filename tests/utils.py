from django.test import TestCase
from django.core.cache import cache

from .models import Play, Poem, Author


class MultipleModelTestCase(TestCase):
    """
    Extends TestCase to add setup needed by all MM tests
    """
    def setUp(self):
        cache.clear()

        Play.objects.bulk_create([
            Play(title='Romeo And Juliet',
                 genre='Tragedy',
                 year=1597,
                 author=Author.objects.create(name='Play Shakespeare 1')),
            Play(title="A Midsummer Night's Dream",
                 genre='Comedy',
                 year=1600,
                 author=Author.objects.create(name='Play Shakespeare 2')),
            Play(title='Julius Caesar',
                 genre='Tragedy',
                 year=1623,
                 author=Author.objects.create(name='Play Shakespeare 3')),
            Play(title='As You Like It',
                 genre='Comedy',
                 year=1623,
                 author=Author.objects.create(name='Play Shakespeare 4'))
        ])

        Poem.objects.bulk_create([
            Poem(title="Shall I compare thee to a summer's day?",
                 style="Sonnet",
                 author=Author.objects.create(name='Poem Shakespeare 1')),
            Poem(title="As a decrepit father takes delight",
                 style="Sonnet",
                 author=Author.objects.create(name='Poem Shakespeare 2')),
            Poem(title="A Lover's Complaint",
                 style="Narrative",
                 author=Author.objects.create(name='Poem Shakespeare 3'))
        ])
