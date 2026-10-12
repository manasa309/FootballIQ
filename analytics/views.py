from django.db.models import Avg, Count, Max, Sum
from django.shortcuts import render

from analytics.models import MatchPerformance
from players.models import Player


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
