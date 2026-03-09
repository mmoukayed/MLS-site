from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("",                views.home,            name="home"),
    path("meet-the-team/",  views.meet_the_team,   name="meet-the-team"),
    path("dashboard/",      views.student_dashboard, name="student_dashboard"),
path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("events/",         views.student_events,  name="events"),

    path("teams/",          views.student_teams,   name="teams"),
    path("teams/<int:team_id>/", views.team_detail, name="team-detail"),
    path("profile/", views.student_profile, name="profile"),
    path("finish-profile/", views.finish_profile, name="finish_profile"),
    path("edit-role/", views.edit_role, name="edit_role"),
    path("delete-member/", views.delete_member, name="delete_member"),
    path("create-event/", views.create_event, name="create_event"),
    path('edit-event/', views.edit_event, name='edit_event'),
    path('delete-event/', views.delete_event, name='delete_event'),

    path('teams/edit/', views.edit_team, name='edit_team'),
    path('teams/delete/', views.admin_delete_team, name='admin_delete_team'),
    path('members/search/', views.search_members, name='search_members'),
]
