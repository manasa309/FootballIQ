# Touchline | FootballIQ

Touchline is a Django football-player network and performance analytics portfolio project. It includes player sign-up and profile editing, a searchable player directory, match-by-match performance records, player analytics, and an admin interface for managing data.

## Run locally

From the project folder in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> for the overview, <http://127.0.0.1:8000/players/> for the searchable directory, <http://127.0.0.1:8000/accounts/signup/> to create a player account, and <http://127.0.0.1:8000/admin/> to manage profiles and match data.

`seed_demo_data` is safe to run more than once. It creates fictional sample players, clubs, a fictional competition, and illustrative performance records; it does not overwrite existing data. Do not present the generated records as real-world football statistics.

## Analytics

Player pages calculate totals and averages from match-level records, including goals, assists, goal contributions per 90 minutes, passing percentage, and an SVG rating trend. The overview ranks players by goals and rating and summarizes all recorded matches. Ratings and profile data are indicative and depend on their source.

## Data model

- `Player` stores public player profile information.
- `MatchPerformance` stores one player's match-level statistics and is editable in Django admin.
- A player can have no match records; the site displays empty analytics states rather than fabricated values.
