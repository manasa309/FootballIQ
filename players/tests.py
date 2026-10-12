from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from analytics.models import MatchPerformance

from .models import Player


class PlayerPagesTests(TestCase):
    def setUp(self):
        self.player = Player.objects.create(
            name="Avery Morgan",
            date_of_birth=date(2002, 5, 14),
            nationality="Canadian",
            position="CM",
            preferred_foot="Right",
            height=178,
            club="Northbridge FC",
            bio="A composed, progressive midfielder.",
        )
        MatchPerformance.objects.create(
            player=self.player,
            match_date=date.today() - timedelta(days=7),
            opponent="Riverside Town",
            goals=1,
            assists=1,
            minutes_played=90,
            pass_completion=88,
            rating=8.2,
        )

    def test_directory_shows_profiles_and_aggregated_metrics(self):
        response = self.client.get(reverse("player_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Avery Morgan")
        self.assertContains(response, "Northbridge FC")
        self.assertContains(response, "8.2")

    def test_directory_search_and_position_filter(self):
        response = self.client.get(
            reverse("player_list"),
            {"q": "Northbridge", "position": "CM"},
        )

        self.assertContains(response, "Avery Morgan")
        self.assertEqual(len(response.context["players"]), 1)

    def test_player_profile_includes_match_analytics(self):
        response = self.client.get(
            reverse("player_detail", args=[self.player.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GOAL CONTRIBUTIONS / 90")
        self.assertContains(response, "Riverside Town")
        self.assertEqual(response.context["totals"]["goals"], 1)
        self.assertEqual(response.context["totals"]["assists"], 1)


class DashboardTests(TestCase):
    def test_dashboard_loads_without_seed_data(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sharper lens.")
        self.assertContains(response, "No match data yet")
