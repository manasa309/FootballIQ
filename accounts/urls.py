from django.urls import path

from .views import (
    PlayerLoginView,
    PlayerLogoutView,
    edit_profile,
    my_profile,
    signup,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", PlayerLoginView.as_view(), name="login"),
    path("logout/", PlayerLogoutView.as_view(), name="logout"),
    path("profile/", my_profile, name="profile"),
    path("profile/edit/", edit_profile, name="profile_edit"),
]
