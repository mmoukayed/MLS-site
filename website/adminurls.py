from django.urls import path
from . import views

app_name = "admin"

url_patterns = [
    path("users/edit-role/", views.edit_role, name="edit_role"),
    path("users/delete/", views.delete_member, name="delete_member"),

    path("events/create/", views.create_event, name="create_event"),
    path('events/edit/', views.edit_event, name='edit_event'),
    path('events/delete/', views.delete_event, name='delete_event'),

    path('teams/edit/', views.edit_team, name='edit_team'),
    path('teams/delete/', views.admin_delete_team, name='admin_delete_team'),
    path('members/search/', views.search_members, name='search_members'),

    path("workshops/create/", views.create_workshop, name="create_workshop"),
    path("workshops/edit/", views.edit_workshop, name="edit_workshop"),
    path("workshops/delete/", views.delete_workshop, name="delete_workshop"),
    path("workshops/status/", views.set_workshop_status, name="set_workshop_status"),
    path("workshops/file/<int:file_id>/", views.download_workshop_file, name="download_workshop_file"),
]
