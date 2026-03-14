from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("meet-the-team/", views.meet_the_team, name="meet-the-team"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),

    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("events/", views.student_events, name="events"),
    path("teams/", views.student_teams, name="teams"),
    path("teams/<int:team_id>/", views.team_detail, name="team-detail"),
    path("profile/", views.student_profile, name="profile"),
    path("finish-profile/", views.finish_profile, name="finish_profile"),
    path("users/edit-role/", views.edit_role, name="edit_role"),
    path("users/delete/", views.delete_member, name="delete_member"),
    path("events/create/", views.create_event, name="create_event"),
    path('events/edit/', views.edit_event, name='edit_event'),
    path('events/delete/', views.delete_event, name='delete_event'),

    path('teams/edit/', views.edit_team, name='edit_team'),
    path('teams/delete/', views.admin_delete_team, name='admin_delete_team'),
    path('members/search/', views.search_members, name='search_members'),
    # Workshop management
    path("workshops/create/", views.create_workshop, name="create_workshop"),
    path("workshops/edit/", views.edit_workshop, name="edit_workshop"),
    path("workshops/delete/", views.delete_workshop, name="delete_workshop"),
    path("workshops/status/", views.set_workshop_status, name="set_workshop_status"),
    path("workshops/file/<int:file_id>/", views.download_workshop_file, name="download_workshop_file"),
]
