import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from analytics.models import MatchPerformance
from players.models import Player


DEMO_PLAYERS = [
    ("Maya Okafor", "CM", "Nigerian", "Harbor City FC", "Right", 170, "A tempo-setting midfielder who thrives between the lines."),
    ("Elias Berg", "ST", "Swedish", "Northbridge FC", "Left", 184, "A sharp finisher with a knack for finding space in the box."),
    ("Sofia Costa", "LW", "Portuguese", "Redwood Athletic", "Right", 165, "A direct wide forward who creates chances at speed."),
    ("Noah Williams", "CB", "English", "Lakeside United", "Right", 186, "A composed defender comfortable building from the back."),
    ("Amara Diallo", "DM", "Senegalese", "Harbor City FC", "Right", 168, "An energetic ball-winner who keeps the team moving."),
    ("Luca Moretti", "AM", "Italian", "Eastvale Rovers", "Left", 176, "A creative playmaker with a quick eye for the final pass."),
    ("Isla Campbell", "GK", "Scottish", "Northbridge FC", "Right", 173, "An assured goalkeeper with strong distribution."),
    ("Mateo Reyes", "RB", "Mexican", "Redwood Athletic", "Right", 178, "An adventurous full-back who brings width and recovery pace."),
]

OPPONENTS = [
    "Riverside Town", "Westmoor City", "Ashford Athletic", "Pinehill FC",
    "Kingswell United", "Southgate Rovers", "Millfield Town", "Oakridge FC",
]


class Command(BaseCommand):
    help = "Create clearly fictional sample players and match performances for a demo."

    def handle(self, *args, **options):
        randomizer = random.Random(2026)
        today = date.today()
        players_created = 0
        performances_created = 0

        for player_index, (
            name,
            position,
            nationality,
            club,
            foot,
            height,
            bio,
        ) in enumerate(DEMO_PLAYERS):
            player, created = Player.objects.get_or_create(
                name=name,
                defaults={
                    "date_of_birth": date(2000 + randomizer.randint(0, 5), 3, 12),
                    "nationality": nationality,
                    "position": position,
                    "preferred_foot": foot,
                    "height": height,
                    "club": club,
                    "bio": bio,
                },
            )
            players_created += int(created)
            for match_number in range(8):
                opponent = OPPONENTS[(match_number + player_index) % len(OPPONENTS)]
                match_date = today - timedelta(days=(7 * (7 - match_number)))
                goal_probability = {
                    "GK": 0.005,
                    "CB": 0.035,
                    "LB": 0.04,
                    "RB": 0.04,
                    "DM": 0.045,
                    "CM": 0.09,
                    "AM": 0.16,
                    "LW": 0.20,
                    "RW": 0.20,
                    "ST": 0.32,
                }[position]
                assist_probability = {
                    "GK": 0.005,
                    "CB": 0.015,
                    "LB": 0.08,
                    "RB": 0.08,
                    "DM": 0.07,
                    "CM": 0.13,
                    "AM": 0.22,
                    "LW": 0.20,
                    "RW": 0.20,
                    "ST": 0.15,
                }[position]
                defensive_role = position in {"CB", "LB", "RB", "DM"}
                _, created = MatchPerformance.objects.get_or_create(
                    player=player,
                    match_date=match_date,
                    opponent=opponent,
                    defaults={
                        "competition": "Continental Development League",
                        "minutes_played": randomizer.choice([63, 78, 84, 90]),
                        "goals": int(randomizer.random() < goal_probability),
                        "assists": int(randomizer.random() < assist_probability),
                        "shots": randomizer.randint(0, 4) if position != "GK" else 0,
                        "key_passes": randomizer.randint(0, 4) if position != "GK" else 0,
                        "tackles": randomizer.randint(1, 6) if defensive_role else randomizer.randint(0, 3),
                        "interceptions": randomizer.randint(1, 5) if defensive_role else randomizer.randint(0, 2),
                        "pass_completion": round(randomizer.uniform(70, 96), 1),
                        "rating": round(randomizer.uniform(6.2, 9.1), 1),
                    },
                )
                performances_created += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo dataset ready: {players_created} new fictional players and "
                f"{performances_created} new match performances."
            )
        )
        self.stdout.write(
            "All names, clubs, competitions, and statistics in this demo dataset are fictional."
        )
