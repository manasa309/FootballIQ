from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from players.models import Player


class PlayerAccountTests(TestCase):
    def signup_data(self):
        return {
            "username": "midfielder42",
            "password1": "Lateral!94Pass",
            "password2": "Lateral!94Pass",
            "name": "Avery Morgan",
            "date_of_birth": "2002-05-14",
            "nationality": "Canadian",
            "position": "CM",
            "preferred_foot": "Right",
            "height": "178",
            "club": "Northbridge FC",
            "bio": "A composed, progressive midfielder.",
        }

    def test_signup_creates_and_signs_in_a_player_profile(self):
        response = self.client.post(reverse("accounts:signup"), self.signup_data())

        player = Player.objects.get(name="Avery Morgan")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("player_detail", args=[player.pk]))
        self.assertEqual(player.user.username, "midfielder42")
        self.assertEqual(player.date_of_birth, date(2002, 5, 14))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_signup_shows_errors_for_invalid_profile_data(self):
        data = self.signup_data()
        data["height"] = "not-a-height"

        response = self.client.post(reverse("accounts:signup"), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a number.")
        self.assertFalse(get_user_model().objects.filter(username="midfielder42").exists())

    def test_only_profile_owner_can_edit_profile(self):
        owner = get_user_model().objects.create_user(
            username="owner",
            password="Lateral!94Pass",
        )
        other_user = get_user_model().objects.create_user(
            username="other",
            password="Lateral!94Pass",
        )
        player = Player.objects.create(
            user=owner,
            name="Avery Morgan",
            date_of_birth=date(2002, 5, 14),
            nationality="Canadian",
            position="CM",
            preferred_foot="Right",
            height=178,
            club="Northbridge FC",
        )
        self.client.force_login(other_user)

        response = self.client.get(reverse("accounts:profile_edit"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(player.club, "Northbridge FC")

    def test_owner_can_update_their_profile(self):
        user = get_user_model().objects.create_user(
            username="owner",
            password="Lateral!94Pass",
        )
        player = Player.objects.create(
            user=user,
            name="Avery Morgan",
            date_of_birth=date(2002, 5, 14),
            nationality="Canadian",
            position="CM",
            preferred_foot="Right",
            height=178,
            club="Northbridge FC",
        )
        self.client.force_login(user)
        data = self.signup_data()
        data.update({"name": "Avery M. Morgan", "club": "Harbor City FC"})

        response = self.client.post(reverse("accounts:profile_edit"), data)

        player.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(player.name, "Avery M. Morgan")
        self.assertEqual(player.club, "Harbor City FC")

    def test_player_can_sign_in_and_sign_out(self):
        user = get_user_model().objects.create_user(
            username="midfielder42",
            password="Lateral!94Pass",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": user.username, "password": "Lateral!94Pass"},
        )
        self.assertRedirects(response, reverse("dashboard"))

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("dashboard"))
        self.assertNotIn("_auth_user_id", self.client.session)
