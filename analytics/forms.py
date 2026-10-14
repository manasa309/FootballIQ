from django import forms

from analytics.models import MatchPerformance
from players.models import Player


class AnalyticsFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    position = forms.ChoiceField(
        required=False,
        choices=[("", "All positions"), *Player.POSITION_CHOICES],
    )
    club = forms.ChoiceField(required=False)
    competition = forms.ChoiceField(required=False)
    min_minutes = forms.IntegerField(required=False, min_value=0)
    players = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Player.objects.none(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["club"].choices = [
            ("", "All clubs"),
            *[(club, club) for club in Player.objects.order_by("club").values_list("club", flat=True).distinct()],
        ]
        self.fields["competition"].choices = [
            ("", "All competitions"),
            *[
                (competition, competition)
                for competition in MatchPerformance.objects.exclude(
                    competition=""
                ).order_by("competition").values_list("competition", flat=True).distinct()
            ],
        ]
        self.fields["players"].queryset = Player.objects.order_by("name")
        self.fields["club"].widget.attrs["aria-label"] = "Filter by club"
        self.fields["competition"].widget.attrs["aria-label"] = "Filter by competition"
        self.fields["min_minutes"].widget.attrs.update(
            {"min": 0, "placeholder": "Any minutes"}
        )
        self.fields["players"].widget.attrs.update(
            {"size": 5, "aria-label": "Players to compare"}
        )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            self.add_error("date_to", "End date must be on or after the start date.")
        return cleaned_data
