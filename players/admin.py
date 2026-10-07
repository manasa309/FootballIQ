from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'position',
        'nationality',
        'club',
        'preferred_foot',
    )

    list_filter = (
        'position',
        'nationality',
        'preferred_foot',
    )

    search_fields = (
        'name',
        'club',
        'nationality',
    )