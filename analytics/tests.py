from io import StringIO
from datetime import date

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

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


class AnalyticsWorkspaceTests(TestCase):
    def setUp(self):
        self.striker_one = self.create_player("Avery Morgan", "ST", "Northbridge FC")
        self.striker_two = self.create_player("Jamie Clarke", "ST", "Riverside FC")
        self.defender = self.create_player("Riley Chen", "CB", "Northbridge FC")
        self.create_performance(
            self.striker_one,
            date(2025, 1, 1),
            "Premier League",
            minutes_played=90,
            goals=1,
            rating=8,
        )
        self.create_performance(
            self.striker_one,
            date(2025, 1, 2),
            "National Cup",
            minutes_played=30,
            goals=1,
            rating=7,
        )
        self.create_performance(
            self.striker_two,
            date(2025, 1, 2),
            "Premier League",
            minutes_played=90,
            goals=1,
            rating=7,
        )
        self.create_performance(
            self.defender,
            date(2025, 1, 2),
            "Premier League",
            minutes_played=90,
            tackles=3,
            rating=8,
        )

    def create_player(self, name, position, club):
        return Player.objects.create(
            name=name,
            date_of_birth=date(2002, 5, 14),
            nationality="Canadian",
            position=position,
            preferred_foot="Right",
            height=178,
            club=club,
        )

    def create_performance(self, player, match_date, competition, **stats):
        return MatchPerformance.objects.create(
            player=player,
            match_date=match_date,
            opponent=f"Opponent {player.name} {match_date}",
            competition=competition,
            **stats,
        )

    def test_analysis_filters_performances_and_groups_position_percentiles(self):
        response = self.client.get(
            reverse("analysis"),
            {
                "date_from": "2025-01-02",
                "date_to": "2025-01-02",
                "position": "ST",
                "club": "Riverside FC",
                "competition": "Premier League",
                "min_minutes": "60",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row["player__name"] for row in response.context["player_rows"]],
            ["Jamie Clarke"],
        )
        self.assertEqual(response.context["summary"]["matches"], 1)

    def test_analysis_compares_players_using_the_same_filters(self):
        response = self.client.get(
            reverse("analysis"),
            {
                "date_from": "2025-01-01",
                "date_to": "2025-01-02",
                "players": [self.striker_one.pk, self.striker_two.pk],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [player["player__name"] for player in response.context["selected_players"]],
            ["Avery Morgan", "Jamie Clarke"],
        )
        self.assertEqual(response.context["selected_players"][0]["appearances"], 2)
        self.assertEqual(
            response.context["selected_players"][0]["goal_contributions_per_90"],
            1.5,
        )
        self.assertEqual(
            response.context["selected_players"][0]["position_percentile"],
            75,
        )
        self.assertEqual(
            response.context["selected_players"][1]["position_percentile"],
            25,
        )
        self.assertEqual(len(response.context["rating_trends"]), 2)
        defender_row = next(
            row
            for row in response.context["player_rows"]
            if row["player_id"] == self.defender.pk
        )
        self.assertEqual(
            defender_row["percentile_metric_label"],
            "interceptions / 90",
        )
        self.assertIsNone(defender_row["position_percentile"])

    def test_players_without_records_in_filter_are_reported(self):
        response = self.client.get(
            reverse("analysis"),
            {
                "position": "ST",
                "players": [self.striker_one.pk, self.defender.pk],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [player.pk for player in response.context["unmatched_players"]],
            [self.defender.pk],
        )
        self.assertContains(response, "These players are excluded from the comparison.")

    def test_analysis_rejects_reversed_date_range(self):
        response = self.client.get(
            reverse("analysis"),
            {"date_from": "2025-01-03", "date_to": "2025-01-01"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["filter_form"].is_valid())
        self.assertIsNone(response.context["summary"])

    def test_theme_picker_is_available_on_analytics_page(self):
        response = self.client.get(reverse("analysis"))

        self.assertContains(response, 'value="light">Light</option>')
        self.assertContains(response, 'value="dark">Dark</option>')
        self.assertContains(response, 'value="lavender">Lavender</option>')
