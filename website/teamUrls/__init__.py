from django.urls import path, include
from website import views

urlpatterns = [
    path('create/',views.create_team),
    path('delete/<int:team_id>/',views.delete_team),
    path('join/<int:team_id>/',views.join_team),
    path('accept/<int:team_id>/<int:user_id>/',views.accept_invite_request),
    path('reject/<int:team_id>/<int:user_id>/',views.reject_invite_request),
    path('leave/<int:team_id>/',views.leave_team),
]