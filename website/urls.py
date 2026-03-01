from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("",                views.home,            name="home"),
    path("meet-the-team/",  views.meet_the_team,   name="meet-the-team"),
    path("dashboard/",      views.student_dashboard, name="student_dashboard"),
    path("events/",         views.student_events,  name="events"),
    path("teams/",          views.student_teams,   name="teams"),
    path("teams/<int:team_id>/", views.team_detail, name="team-detail"),
    path("profile/",        views.student_profile, name="profile"),
]
