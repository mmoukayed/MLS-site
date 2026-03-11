from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from .auth_utils import normalize_rit_email
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

User = get_user_model()

def _log(action, message):
    """Lazy import to avoid circular dependency: accounts → website."""
    try:
        from website.models import ActivityLog
        ActivityLog.objects.create(action=action, message=message)
    except Exception:
        pass

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
        is_new = sociallogin.user.pk is None

        user = super().save_user(request, sociallogin, form)

        if is_new:
            request.session["incomplete_profile"] = True
            _log(
                "user_registered",
                f"New member registered via Google: {user.first_name} {user.last_name} ({user.email})",
            )

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