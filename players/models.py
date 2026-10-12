from django.db import models
from django.conf import settings


class Player(models.Model):

    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('CB', 'Centre Back'),
        ('LB', 'Left Back'),
        ('RB', 'Right Back'),
        ('DM', 'Defensive Midfielder'),
        ('CM', 'Central Midfielder'),
        ('AM', 'Attacking Midfielder'),
        ('LW', 'Left Winger'),
        ('RW', 'Right Winger'),
        ('ST', 'Striker'),
    ]

    name = models.CharField(max_length=100)

    date_of_birth = models.DateField()

    nationality = models.CharField(max_length=100)

    position = models.CharField(
        max_length=2,
        choices=POSITION_CHOICES
    )

    preferred_foot = models.CharField(
        max_length=10,
        choices=[
            ('Left', 'Left'),
            ('Right', 'Right'),
        ]
    )

    height = models.FloatField(
        help_text="Height in centimeters"
    )

    club = models.CharField(max_length=100)

    profile_image = models.ImageField(
        upload_to='players/',
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="player_profile",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name