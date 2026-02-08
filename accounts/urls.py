from django.urls import path
from .views import (
    request_login,
    magic_login,
    otp_login,
    login_page,
    otp_page,
    signup,
    logout_view,
    resend_otp
)

urlpatterns = [
    # Pages
    path("login/", login_page, name="login"),
    path("otp/", otp_page, name="otp"),
    path("signup/", signup, name="signup"),

    # API endpoints
    path("request-login/", request_login, name="request_login"),
    path("resend-otp/", resend_otp, name="resend_otp"),
    path("otp-login/", otp_login, name="otp_login"),
    path("magic-login/", magic_login, name="magic_login"),
    path("logout/", logout_view, name="logout"),
]