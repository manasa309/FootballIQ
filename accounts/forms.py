from django import forms
from django.contrib.auth.forms import UserCreationForm

from players.models import Player


class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = (
            "name",
            "date_of_birth",
            "nationality",
            "position",
            "preferred_foot",
            "height",
            "club",
            "profile_image",
            "bio",
        )
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class PlayerSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("username",)
