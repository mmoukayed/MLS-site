from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from .auth_utils import normalize_rit_email
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get("email")
        if not email:
            return

        email = normalize_rit_email(email)

        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            request.session["incomplete_profile"] = True


    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Detect brand new Google signup
        if user._state.adding:
            request.session["incomplete_profile"] = True

        return user

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        print("LOGIN REDIRECT RUNNING")
        if request.session.pop("incomplete_profile", False):
            return reverse("website:finish_profile")

        return reverse("website:student_dashboard")

    def get_signup_redirect_url(self, request):
        print("SIGNUP REDIRECT RUNNING")
        return reverse("website:finish_profile")