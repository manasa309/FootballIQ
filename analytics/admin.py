from django.contrib import admin

from .models import MatchPerformance


@admin.register(MatchPerformance)
class MatchPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "match_date",
        "opponent",
        "goals",
        "assists",
        "rating",
    )
    list_filter = ("match_date", "competition", "player__position")
    search_fields = ("player__name", "opponent", "competition")
    date_hierarchy = "match_date"
