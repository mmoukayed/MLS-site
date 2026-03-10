from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_team, name="team-create"),
    path("<int:team_id>/leave/", views.leave_team, name="team-leave"),
    path("<int:team_id>/delete/", views.delete_team, name="team-delete"),
    path("<int:team_id>/join/", views.join_team, name="team-join"),
    path("<int:team_id>/cancel/", views.cancel_join_request, name="team-cancel-join"),
    path("<int:team_id>/accept/<int:user_id>/", views.accept_join_request, name="team-join-request-accept"),
    path("<int:team_id>/reject/<int:user_id>/", views.reject_join_request, name="team-join-request-reject"),
    path("<int:team_id>/invite/accept/", views.accept_invite, name="team-invite-accept"),
    path("<int:team_id>/invite/reject/", views.reject_invite, name="team-invite-reject"),
    path("<int:team_id>/invite/<int:user_id>/", views.invite_member, name="team-invite"),
    path("<int:team_id>/remove/<int:user_id>/", views.remove_member, name="team-remove-member"),
    path("<int:team_id>/promote/<int:user_id>/", views.promote_member, name="team-promote-member"),
    path("<int:team_id>/demote/<int:user_id>/", views.demote_member, name="team-demote-member"),

]
