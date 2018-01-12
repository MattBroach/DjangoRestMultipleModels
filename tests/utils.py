from django.test import TestCase
from django.core.cache import cache

from .models import Play, Poem


class MultipleModelTestCase(TestCase):
    """
    Extends TestCase to add setup needed by all MM tests
    """
    def setUp(self):
        cache.clear()

        Play.objects.bulk_create([
            Play(title='Romeo And Juliet',
                 genre='Tragedy',
                 year=1597),
            Play(title="A Midsummer Night's Dream",
                 genre='Comedy',
                 year=1600),
            Play(title='Julius Caesar',
                 genre='Tragedy',
                 year=1623),
            Play(title='As You Like It',
                 genre='Comedy',
                 year=1623)
        ])

        Poem.objects.bulk_create([
            Poem(title="Shall I compare thee to a summer's day?",
                 style="Sonnet"),
            Poem(title="As a decrepit father takes delight",
                 style="Sonnet"),
            Poem(title="A Lover's Complaint",
                 style="Narrative")
        ])
