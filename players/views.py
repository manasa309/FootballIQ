from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import render, get_object_or_404

from analytics.models import MatchPerformance

from .models import Player


def player_list(request):

    query = request.GET.get("q", "").strip()
    position = request.GET.get("position", "").strip()
    players = Player.objects.annotate(
        appearances=Count("performances"),
        total_goals=Sum("performances__goals"),
        total_assists=Sum("performances__assists"),
        average_rating=Avg("performances__rating"),
    )
    if query:
        players = players.filter(
            Q(name__icontains=query)
            | Q(club__icontains=query)
            | Q(nationality__icontains=query)
        )
    if position:
        players = players.filter(position=position)
    players = players.order_by("name")
    return render(
        request,
        'players/player_list.html',
        {
            "players": players,
            "query": query,
            "selected_position": position,
            "positions": Player.POSITION_CHOICES,
        },
    )


def player_detail(request, player_id):

    player = get_object_or_404(Player, id=player_id)
    performance_query = MatchPerformance.objects.filter(player=player)
    recent_performances = list(
        performance_query.order_by("-match_date", "-id")[:8]
    )
    chart = list(reversed(recent_performances))
    totals = performance_query.aggregate(
        appearances=Count("id"),
        minutes=Sum("minutes_played"),
        goals=Sum("goals"),
        assists=Sum("assists"),
        shots=Sum("shots"),
        key_passes=Sum("key_passes"),
        tackles=Sum("tackles"),
        interceptions=Sum("interceptions"),
        pass_completion=Avg("pass_completion"),
        rating=Avg("rating"),
    )
    minutes = totals["minutes"] or 0
    totals["goal_contributions_per_90"] = (
        ((totals["goals"] or 0) + (totals["assists"] or 0)) * 90 / minutes
        if minutes
        else 0
    )
    chart_points = []
    if chart:
        for index, performance in enumerate(chart):
            x = 12 + (index * 276 / max(len(chart) - 1, 1))
            y = 86 - (max(5, min(performance.rating, 10)) - 5) / 5 * 76
            chart_points.append(
                {
                    "x": round(x, 1),
                    "y": round(y, 1),
                    "rating": performance.rating,
                    "date": performance.match_date,
                    "opponent": performance.opponent,
                }
            )

    return render(
        request,
        'players/player_detail.html',
        {
            "player": player,
            "totals": totals,
            "performances": recent_performances,
            "chart_points": chart_points,
            "chart_line": " ".join(
                f'{point["x"]},{point["y"]}' for point in chart_points
            ),
        },
    )