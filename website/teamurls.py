from django.urls import path
from . import views

urlpatterns = [
    path("create/",                                  views.create_team,           name="team-create"),
    path("<int:team_id>/delete/",                    views.delete_team,           name="team-delete"),
    path("<int:team_id>/join/",                      views.join_team,             name="team-join"),
    path("<int:team_id>/leave/",                     views.leave_team,            name="team-leave"),
    path("<int:team_id>/accept/<int:user_id>/",      views.accept_invite_request, name="team-accept"),
    path("<int:team_id>/reject/<int:user_id>/",      views.reject_invite_request, name="team-reject"),
]

