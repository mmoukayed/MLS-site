from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/",  admin.site.urls),

    # ── Website pages (home, dashboard, teams, events, profile, meet-the-team)
    path("",        include("website.urls")),

    # ── Auth (login, signup, OTP, magic-link, logout)
    path("auth/",   include("accounts.urls", namespace="accounts")),

    # ── Team API endpoints  (/team/create/, /team/<id>/join/, etc.)
    path("team/",   include("website.teamurls")),
]