from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from analytics.models import MatchPerformance
from players.models import Player


class SeedDemoDataTests(TestCase):
    def test_seed_command_is_repeatable_and_creates_fictional_data(self):
        call_command("seed_demo_data", stdout=StringIO())
        initial_player_count = Player.objects.count()
        initial_performance_count = MatchPerformance.objects.count()

        call_command("seed_demo_data", stdout=StringIO())

        self.assertEqual(initial_player_count, 8)
        self.assertEqual(initial_performance_count, 64)
        self.assertEqual(Player.objects.count(), initial_player_count)
        self.assertEqual(MatchPerformance.objects.count(), initial_performance_count)
        self.assertEqual(
            MatchPerformance.objects.values("competition").distinct().get()["competition"],
            "Continental Development League",
        )
