from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from players.models import Player

from .forms import PlayerProfileForm, PlayerSignupForm


class PlayerLoginView(LoginView):
    template_name = "accounts/login.html"


class PlayerLogoutView(LogoutView):
    next_page = "dashboard"


def signup(request):
    account_form = PlayerSignupForm(request.POST or None)
    profile_form = PlayerProfileForm(
        request.POST or None,
        request.FILES or None,
    )
    if request.method == "POST":
        account_is_valid = account_form.is_valid()
        profile_is_valid = profile_form.is_valid()
        if account_is_valid and profile_is_valid:
            with transaction.atomic():
                user = account_form.save()
                player = profile_form.save(commit=False)
                player.user = user
                player.save()
            login(request, user)
            messages.success(request, "Your player profile is live. Welcome to Touchline.")
            return redirect("player_detail", player_id=player.pk)

    return render(
        request,
        "accounts/signup.html",
        {
            "account_form": account_form,
            "profile_form": profile_form,
        },
    )


@login_required
def my_profile(request):
    player = get_object_or_404(Player, user=request.user)
    return redirect("player_detail", player_id=player.pk)


@login_required
def edit_profile(request):
    player = get_object_or_404(Player, user=request.user)
    profile_form = PlayerProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=player,
    )
    if request.method == "POST" and profile_form.is_valid():
        profile_form.save()
        messages.success(request, "Your player profile has been updated.")
        return redirect("player_detail", player_id=player.pk)

    return render(
        request,
        "accounts/profile_edit.html",
        {"profile_form": profile_form, "player": player},
    )
