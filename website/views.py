import json

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseNotAllowed
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from website import models
from accounts.models import Member


# ════════════════════════════════════════════════════════════
#  PAGE VIEWS
# ════════════════════════════════════════════════════════════

def home(request):
    # prereqData context processor provides majors + nationalities globally
    return render(request, "index.html")


def meet_the_team(request):
    return render(request, "meettheteam.html")


@login_required(login_url="/")
def student_dashboard(request: WSGIRequest):
    if not request.user.is_authenticated:
        # return HttpResponse(json.dumps({"message": "Not Logged In","error":20}),status=401)
        return redirect("/")
    joined_teams = []
    owned_teams = []
    invited_teams = []
    pending_teams = []
    for team in models.Team.objects.all():
        if team.team_members.contains(request.user):
            joined_teams.append(team)
        if team.team_leaders.contains(request.user):
            owned_teams.append(team)
        if team.invited_members.contains(request.user):
            invited_teams.append(team)
        if team.pending_members.contains(request.user):
            pending_teams.append(team)    
    print(len(invited_teams))
    return render(request, "student-dashboard.html",{"joined_teams": joined_teams, "owned_teams": owned_teams, "pending_teams": pending_teams, "invited_teams": invited_teams, "events": models.Event.objects.all()})



@login_required(login_url="/")
def student_events(request: WSGIRequest):
    return render(request, "student-events.html")


@login_required(login_url="/")
def student_teams(request: WSGIRequest):
    joined_teams = []
    pending_teams = []
    for team in models.Team.objects.all():
        if request.user in team.team_leaders.all() or request.user in team.team_members.all():
            joined_teams.append(team)
        elif request.user in team.pending_members.all():
            pending_teams.append(team)
    return render(request, "student-teams.html", {"teams": models.Team.objects.all(), "joined_teams": joined_teams, "pending_teams": pending_teams})


@login_required(login_url="/")
def team_detail(request: WSGIRequest, team_id: int):
    try:
        team = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        return redirect("website:teams")
    return render(request, "team-detail.html", {"team": team})


@login_required(login_url="/")
def student_profile(request: WSGIRequest):
    return render(request, "student-profile.html")


# ════════════════════════════════════════════════════════════
#  TEAM API ENDPOINTS
# ════════════════════════════════════════════════════════════

@login_required(login_url="/")
@require_http_methods(["POST"])
def create_team(request: WSGIRequest):
    name        = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()

    if not name:
        return JsonResponse({"message": "Team name is required", "error": 40}, status=400)

    team = models.Team(name=name, description=description)
    team.save()
    team.team_leaders.add(request.user)
    team.save()

    return JsonResponse({"message": "Team created successfully", "error": 10, "team_id": team.pk})


@login_required(login_url="/")
@require_http_methods(["DELETE"])
def delete_team(request: WSGIRequest, team_id: int):
    try:
        team = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.team_leaders.contains(request.user):
        return JsonResponse({"message": "Not authorised", "error": 32}, status=403)

    team.delete()
    return JsonResponse({"message": "Team deleted successfully", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def join_team(request: WSGIRequest, team_id: int):
    try:
        team = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if team.team_members.contains(request.user) or team.team_leaders.contains(request.user):
        return JsonResponse({"message": "Already in team", "error": 33}, status=409)

    if team.pending_members.contains(request.user):
        return JsonResponse({"message": "Request already sent", "error": 35}, status=409)

    team.pending_members.add(request.user)
    return JsonResponse({"message": "Join request sent", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def accept_invite_request(request: WSGIRequest, team_id: int, user_id: int):
    try:
        team = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.team_leaders.contains(request.user):
        return JsonResponse({"message": "Not authorised", "error": 32}, status=403)

    try:
        member = Member.objects.get(pk=user_id)
    except Member.DoesNotExist:
        return JsonResponse({"message": "Member not found", "error": 50}, status=404)

    if not team.pending_members.contains(member):
        return JsonResponse({"message": "Member did not request to join", "error": 34}, status=400)

    if team.team_members.contains(member):
        return JsonResponse({"message": "Member already in team", "error": 33}, status=409)

    team.team_members.add(member)
    team.pending_members.remove(member)

    return JsonResponse({"message": "Member added successfully", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def reject_invite_request(request: WSGIRequest, team_id: int, user_id: int):
    try:
        team = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.team_leaders.contains(request.user):
        return JsonResponse({"message": "Not authorised", "error": 32}, status=403)

    try:
        member = Member.objects.get(pk=user_id)
    except Member.DoesNotExist:
        return JsonResponse({"message": "Member not found", "error": 50}, status=404)

    if not team.pending_members.contains(member):
        return JsonResponse({"message": "Member did not request to join", "error": 34}, status=400)

    team.pending_members.remove(member)
    return JsonResponse({"message": "Request rejected", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def leave_team(request: WSGIRequest, team_id: int):
    try:
        team = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.team_members.contains(request.user):
        return JsonResponse({"message": "Not in team", "error": 36}, status=400)

    team.team_members.remove(request.user)
    return JsonResponse({"message": "Left team successfully", "error": 10})