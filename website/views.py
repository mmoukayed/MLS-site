import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth import get_user_model



from website import models
from accounts.models import Member, Major
from django_countries import countries

User = get_user_model()

# ════════════════════════════════════════════════════════════
#  PAGE VIEWS
# ════════════════════════════════════════════════════════════

def home(request):
    # prereqData context processor provides majors + nationalities globally
    return render(request, "index.html")


def meet_the_team(request):
    return render(request, "meettheteam.html")

def admin_dashboard(request):
    members = Member.objects.select_related("major").all()

    return render(request, "admin-dashboard.html", {
        "members": members
    })


@login_required(login_url="/")
def student_dashboard(request: WSGIRequest):
    if not request.user.is_authenticated:
        # return HttpResponse(json.dumps({"message": "Not Logged In","error":20}),status=401)
        return redirect("/")
    teams = []
    for team in models.Team.objects.all():
        if request.user in team.team_members.all() or request.user in team.team_leaders.all() or request.user in team.pending_members.all() or request.user in team.invited_members.all() or request.user == team.creator:
            teams.append(team)
    return render(request, "student-dashboard.html",{"teams": teams, "events": models.Event.objects.all()})



@login_required(login_url="/")
def student_events(request: WSGIRequest):
    return render(request, "student-events.html")


@login_required(login_url="/")
def student_teams(request: WSGIRequest):
    joined_teams = []
    invited_teams = []
    for team in models.Team.objects.all():
        if request.user in team.team_leaders.all() or request.user in team.team_members.all() or request.user == team.creator or request.user in team.pending_members.all():
            joined_teams.append(team)
        elif request.user in team.invited_members.all():
            invited_teams.append(team)
    return render(request, "student-teams.html", {"teams": models.Team.objects.all(), "joined_teams": joined_teams, "invited_teams": invited_teams})


@login_required(login_url="/")
def team_detail(request: WSGIRequest, team_id: int):
    team = get_object_or_404(models.Team, pk=team_id)
    op = False
    if request.user in team.team_leaders.all() or request.user == team.creator:
        op = True
    return render(request, "team-detail.html", {"team": team, "op": op})


@login_required(login_url="/")
def student_profile(request: WSGIRequest):
    is_admin = request.GET.get("admin") == "true"
    return render(request, "student-profile.html",{
        "is_admin": is_admin
    })


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


@login_required(login_url="/")
@require_http_methods(["GET", "POST"])
def finish_profile(request):
    user = request.user
    majors = Major.objects.all()
    if request.method == "POST":
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.date_of_birth = request.POST.get("dob", user.date_of_birth)
        user.gender = request.POST.get("gender", user.gender)
        user.major_id = request.POST.get("field_of_study") or user.major_id
        user.graduation_year = request.POST.get("graduation_year", user.graduation_year)
        user.nationality = request.POST.get("nationality", user.nationality)
        user.save()
        return redirect("website:profile")  # after completion

    return render(request, "../templates/finish-profile.html", {
        "user": user,
        "majors": Major.objects.all(),
        "nationalities": countries,
    })

@user_passes_test(lambda u: u.is_staff)
def edit_role(request):
    if request.method == "POST":
        email = request.POST.get("email")
        is_staff = request.POST.get("is_staff") == "True"
        try:
            user = Member.objects.get(email=email)
            user.is_staff = is_staff
            user.save()
        except Member.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))

@user_passes_test(lambda u: u.is_staff)
def delete_member(request):

    if request.method == "POST":

        email = request.POST.get("email")

        try:
            user = Member.objects.get(email=email)
            user.delete()
        except Member.DoesNotExist:
            pass

    return redirect(request.META.get('HTTP_REFERER', '/'))