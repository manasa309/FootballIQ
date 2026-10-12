from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from players.models import Player


class MatchPerformance(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="performances",
    )
    match_date = models.DateField()
    opponent = models.CharField(max_length=100)
    competition = models.CharField(max_length=120, blank=True)
    minutes_played = models.PositiveSmallIntegerField(default=90)
    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)
    shots = models.PositiveSmallIntegerField(default=0)
    key_passes = models.PositiveSmallIntegerField(default=0)
    tackles = models.PositiveSmallIntegerField(default=0)
    interceptions = models.PositiveSmallIntegerField(default=0)
    pass_completion = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pass completion percentage",
    )
    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Performance rating out of 10",
    )

    class Meta:
        ordering = ["-match_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "match_date", "opponent"],
                name="unique_player_match",
            ),
        ]

    def __str__(self):
        return f"{self.player.name} vs {self.opponent} ({self.match_date})"
