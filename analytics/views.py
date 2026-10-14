from django.db.models import Avg, Count, Max, Sum
from django.shortcuts import render

from analytics.models import MatchPerformance
from players.models import Player

from .forms import AnalyticsFilterForm


POSITION_GROUPS = {
    "GK": "Goalkeeper",
    "CB": "Defence",
    "LB": "Defence",
    "RB": "Defence",
    "DM": "Midfield",
    "CM": "Midfield",
    "AM": "Midfield",
    "LW": "Attack",
    "RW": "Attack",
    "ST": "Attack",
}
POSITION_PERCENTILE_METRICS = {
    "Goalkeeper": ("average_rating", "rating / 10"),
    "Defence": ("interceptions_per_90", "interceptions / 90"),
    "Midfield": ("key_passes_per_90", "key passes / 90"),
    "Attack": ("goal_contributions_per_90", "goals + assists / 90"),
}


def dashboard(request):
    season = MatchPerformance.objects.aggregate(
        matches=Count("id"),
        goals=Sum("goals"),
        assists=Sum("assists"),
        average_rating=Avg("rating"),
        players=Count("player", distinct=True),
        best_rating=Max("rating"),
    )
    leaders = (
        Player.objects.annotate(
            total_goals=Sum("performances__goals"),
            total_assists=Sum("performances__assists"),
            average_rating=Avg("performances__rating"),
            appearances=Count("performances"),
        )
        .filter(appearances__gt=0)
        .order_by("-total_goals", "-average_rating", "name")[:5]
    )
    recent_performances = MatchPerformance.objects.select_related("player")[:6]
    total_players = Player.objects.count()

    context = {
        "season": season,
        "leaders": leaders,
        "recent_performances": recent_performances,
        "total_players": total_players,
        "average_rating": season["average_rating"] or 0,
    }
    return render(request, "analytics/dashboard.html", context)


def analysis(request):
    filter_form = AnalyticsFilterForm(request.GET)
    performances = MatchPerformance.objects.select_related("player")
    player_rows = []
    selected_players = []
    unmatched_players = []
    rating_trends = []
    summary = None

    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        if filters["date_from"]:
            performances = performances.filter(match_date__gte=filters["date_from"])
        if filters["date_to"]:
            performances = performances.filter(match_date__lte=filters["date_to"])
        if filters["position"]:
            performances = performances.filter(player__position=filters["position"])
        if filters["club"]:
            performances = performances.filter(player__club=filters["club"])
        if filters["competition"]:
            performances = performances.filter(competition=filters["competition"])
        if filters["min_minutes"] is not None:
            performances = performances.filter(
                minutes_played__gte=filters["min_minutes"]
            )

        summary = performances.aggregate(
            matches=Count("id"),
            minutes=Sum("minutes_played"),
            goals=Sum("goals"),
            assists=Sum("assists"),
            average_rating=Avg("rating"),
        )
        player_rows = list(
            performances.values(
                "player_id",
                "player__name",
                "player__position",
                "player__club",
            )
            .annotate(
                appearances=Count("id"),
                minutes=Sum("minutes_played"),
                goals=Sum("goals"),
                assists=Sum("assists"),
                shots=Sum("shots"),
                key_passes=Sum("key_passes"),
                tackles=Sum("tackles"),
                interceptions=Sum("interceptions"),
                average_pass_completion=Avg("pass_completion"),
                average_rating=Avg("rating"),
            )
            .order_by("player__name")
        )

        for player in player_rows:
            minutes = player["minutes"] or 0
            player["position_group"] = POSITION_GROUPS[player["player__position"]]
            player["goal_contributions_per_90"] = (
                ((player["goals"] or 0) + (player["assists"] or 0)) * 90 / minutes
                if minutes
                else 0
            )
            for stat in ("goals", "assists", "shots", "key_passes", "tackles", "interceptions"):
                player[f"{stat}_per_90"] = (
                    (player[stat] or 0) * 90 / minutes if minutes else 0
                )

        group_values = {}
        for player in player_rows:
            metric, metric_label = POSITION_PERCENTILE_METRICS[
                player["position_group"]
            ]
            player["percentile_metric"] = metric
            player["percentile_metric_label"] = metric_label
            group_values.setdefault(player["position_group"], []).append(
                player[metric] or 0
            )
        for player in player_rows:
            peers = group_values[player["position_group"]]
            player["position_peer_count"] = len(peers)
            if len(peers) < 2:
                player["position_percentile"] = None
            else:
                score = player[player["percentile_metric"]] or 0
                below = sum(value < score for value in peers)
                equal = sum(value == score for value in peers)
                player["position_percentile"] = round(
                    (below + (equal / 2)) * 100 / len(peers)
                )
            player["goal_contributions_per_90"] = round(
                player["goal_contributions_per_90"], 2
            )
            for stat in ("goals", "assists", "shots", "key_passes", "tackles", "interceptions"):
                player[f"{stat}_per_90"] = round(player[f"{stat}_per_90"], 2)

        player_rows.sort(
            key=lambda player: (
                player["position_group"],
                -player["goal_contributions_per_90"],
                -(player["average_rating"] or 0),
                player["player__name"].casefold(),
            )
        )
        matching_players = {player["player_id"]: player for player in player_rows}
        requested_players = list(filters["players"])
        selected_players = [
            matching_players[player.pk]
            for player in requested_players
            if player.pk in matching_players
        ]
        unmatched_players = [
            player
            for player in requested_players
            if player.pk not in matching_players
        ]

        if len(selected_players) >= 2:
            for player in selected_players:
                recent_ratings = list(
                    performances.filter(player_id=player["player_id"])
                    .order_by("-match_date", "-id")
                    .values("match_date", "rating")[:10]
                )
                recent_ratings.reverse()
                points = []
                for index, performance in enumerate(recent_ratings):
                    x = 12 + (index * 276 / max(len(recent_ratings) - 1, 1))
                    y = 86 - (max(5, min(performance["rating"], 10)) - 5) / 5 * 76
                    points.append(f"{round(x, 1)},{round(y, 1)}")
                rating_trends.append(
                    {
                        "name": player["player__name"],
                        "points": " ".join(points),
                    }
                )

    context = {
        "filter_form": filter_form,
        "player_rows": player_rows,
        "selected_players": selected_players,
        "unmatched_players": unmatched_players,
        "rating_trends": rating_trends,
        "summary": summary,
    }
    return render(request, "analytics/analysis.html", context)
