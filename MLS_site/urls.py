from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/",  admin.site.urls),

    # ── Website pages (home, dashboard, teams, events, profile, meet-the-team)
    path("",        include("website.urls")),

    # ── Auth (login, signup, OTP, magic-link, logout)
    path("auth/",   include("accounts.urls", namespace="accounts")),

    path("accounts/", include("allauth.urls")),

    # ── Team API endpoints  (/team/create/, /team/<id>/join/, etc.)
    path("team/",   include("website.teamurls")),
    
    # ── Event API endpoints  (/event/create/, /event/<id>/join/, etc.)
    path("event/",   include("website.eventurls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
