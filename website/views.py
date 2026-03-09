from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth import get_user_model


from website.models import Event, Team
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
    events  = Event.objects.all().order_by("date", "start_time")
    teams_qs = Team.objects.prefetch_related("team_members", "team_leaders").all()

    teams = []
    for team in teams_qs:
        leaders_str = ", ".join(
            f"{l.first_name} {l.last_name}" for l in team.team_leaders.all()
        ) or "No leader"
        leaders_list = [
            f"{l.first_name} {l.last_name}" for l in team.team_leaders.all()
        ]
        members_list = [
            f"{m.first_name} {m.last_name}" for m in team.team_members.all()
        ]

        teams.append({
            "obj":          team,
            "leaders_str":  leaders_str,
            "member_count": team.team_members.count(),
            "leader_count": team.team_leaders.count(),
            "leaders_json": json.dumps(leaders_list),
            "members_json": json.dumps(members_list),
        })

    return render(request, "admin-dashboard.html", {
        "members": members,
        "events":  events,
        "teams":   teams,
    })


@login_required(login_url="/")
def student_dashboard(request: WSGIRequest):
    if not request.user.is_authenticated:
        # return HttpResponse(json.dumps({"message": "Not Logged In","error":20}),status=401)
        return redirect("/")
    teams = []
    for team in Team.objects.all():
        if request.user in team.team_members.all() or request.user in team.team_leaders.all() or request.user in team.pending_members.all() or request.user in team.invited_members.all() or request.user == team.creator:
            teams.append(team)
    return render(request, "student-dashboard.html",{"teams": teams, "events": Event.objects.all()})



@login_required(login_url="/")
def student_events(request: WSGIRequest):
    return render(request, "student-events.html", {'events': Event.objects.all()})


@login_required(login_url="/")
def student_teams(request: WSGIRequest):
    joined_teams = []
    invited_teams = []
    for team in Team.objects.all():
        if request.user in team.team_leaders.all() or request.user in team.team_members.all() or request.user == team.creator or request.user in team.pending_members.all():
            joined_teams.append(team)
        elif request.user in team.invited_members.all():
            invited_teams.append(team)
    return render(request, "student-teams.html", {"teams": Team.objects.all(), "joined_teams": joined_teams, "invited_teams": invited_teams})


@login_required(login_url="/")
def team_detail(request: WSGIRequest, team_id: int):
    team = get_object_or_404(Team, pk=team_id)
    op = False
    if request.user in team.team_leaders.all() or request.user == team.creator:
        op = True
    return render(request, "team-detail.html", {"team": team, "op": op, "users": Member.objects.all()})


@login_required(login_url="/")
def student_profile(request: WSGIRequest):
    is_admin = request.GET.get("admin") == "true"
    if request.method == "GET":
        return render(request, "student-profile.html",{
            "is_admin": is_admin
        })
    elif request.method == "POST":
        user: Member = request.user
        postreq = request.POST
        print(postreq)
        user.first_name = postreq.get("first_name")
        user.last_name = postreq.get("last_name")
        user.graduation_year = postreq.get("graduation_year")
        user.date_of_birth = postreq.get("dob")
        user.major = Major.objects.get(pk=postreq.get("field_of_study"))
        user.gender = postreq.get("gender")
        user.nationality = postreq.get("nationality")
        user.save()
        return redirect("/profile#success")
    return JsonResponse({"message":"Method not allowed"},status=405)




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

    team = Team(name=name, description=description, creator=request.user)

    team.save()
    team.team_leaders.add(request.user)
    team.save()
# TODO: Change to redirect
    return JsonResponse({"message": "Team created successfully", "error": 10, "team_id": team.pk})


@login_required(login_url="/")
@require_http_methods(["DELETE"])
def delete_team(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not (team.team_leaders.contains(request.user) or request.user == team.creator):
        return JsonResponse({"message": "Not authorized", "error": 32}, status=403)

    team.delete()
    return JsonResponse({"message": "Team deleted successfully", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def join_team(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if team.team_members.contains(request.user) or team.team_leaders.contains(request.user) or request.user == team.creator:
        return JsonResponse({"message": "Already in team", "error": 33}, status=409)

    if team.pending_members.contains(request.user):
        return JsonResponse({"message": "Request already sent", "error": 35}, status=409)

    team.pending_members.add(request.user)
    return JsonResponse({"message": "Join request sent", "error": 10})

@login_required(login_url="/")
@require_http_methods(["POST"])
def cancel_join_request(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)
    
    if not team.pending_members.contains(request.user):
        return JsonResponse({"message": "Not previously requested already", "error": 35}, status=409)

    team.pending_members.remove(request.user)
    return JsonResponse({"message": "Join request cancelled", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def accept_join_request(request: WSGIRequest, team_id: int, user_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not (team.team_leaders.contains(request.user) or request.user == team.creator):
        return JsonResponse({"message": "Not authorized", "error": 32}, status=403)

    try:
        member = Member.objects.get(pk=user_id)
    except Member.DoesNotExist:
        return JsonResponse({"message": "Member not found", "error": 50}, status=404)

    if not team.pending_members.contains(member):
        return JsonResponse({"message": "Member did not request to join", "error": 34}, status=400)

    if team.team_members.contains(member) or team.team_leaders.contains(member):
        return JsonResponse({"message": "Member already in team", "error": 33}, status=409)

    team.team_members.add(member)
    team.pending_members.remove(member)

    return JsonResponse({"message": "Member added successfully", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def reject_join_request(request: WSGIRequest, team_id: int, user_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not (team.team_leaders.contains(request.user) or request.user == team.creator):
        return JsonResponse({"message": "Not authorized", "error": 32}, status=403)

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
def accept_invite(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.invited_members.contains(request.user):
        return JsonResponse({"message": "You were not invited to this team", "error": 32}, status=403)

    team.team_members.add(request.user)
    team.invited_members.remove(request.user)

    return JsonResponse({"message": "Joined Team Successfully", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def reject_invite(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.invited_members.contains(request.user):
        return JsonResponse({"message": "You were not invited to this team", "error": 32}, status=403)

    team.invited_members.remove(request.user)

    return JsonResponse({"message": "Invitation rejected", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def leave_team(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.team_members.contains(request.user) or not team.team_leaders.contains(request.user):
        return JsonResponse({"message": "Not in team", "error": 36}, status=400)

    team.team_members.remove(request.user)
    team.team_leaders.remove(request.user)
    return JsonResponse({"message": "Left team successfully", "error": 10})

@login_required(login_url="/")
@require_http_methods(["POST"])
def invite_member(request: WSGIRequest, team_id: int, user_id: int):
    
    try:
        team = Team.objects.get(pk=team_id)
        user = Member.objects.get(pk=user_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)
    except Member.DoesNotExist:
        return JsonResponse({"message": "User not found", "error": 30}, status=404)
    
    if not (team.team_leaders.contains(request.user) or request.user == team.creator):
        return JsonResponse({"message": "Not authorized", "error": 32}, status=403)
    
    if team.team_members.contains(user) or team.team_leaders.contains(user) or team.creator == user:
        return JsonResponse({"message": "Already in team", "error": 36}, status=400)

    team.invited_members.add(user)
    return JsonResponse({"message": "Invitation Sent Successfully!", "error": 10})

@login_required(login_url="/")
@require_http_methods(["POST"])
def remove_member(request: WSGIRequest, team_id: int, user_id: int):
    try:
        team = Team.objects.get(pk=team_id)
        user = Member.objects.get(pk=user_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)
    except Member.DoesNotExist:
        return JsonResponse({"message": "User not found", "error": 30}, status=404)

    if not (team.team_leaders.contains(request.user) or request.user == team.creator):
        return JsonResponse({"message": "Not authorized", "error": 32}, status=403)

    if not (team.team_members.contains(user) or team.team_leaders.contains(user)):
        return JsonResponse({"message": "User not in team", "error": 10}, status=400)
    
    team.team_members.remove(user)
    team.team_leaders.remove(user)
    team.invited_members.remove(user)
    team.pending_members.remove(user)
    return JsonResponse({"message": "Team member removed!", "error": 36})


@login_required(login_url="/")
@require_http_methods(["POST"])
def promote_member(request: WSGIRequest, team_id: int, user_id: int):
    try:
        team = Team.objects.get(pk=team_id)
        user = Member.objects.get(pk=user_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)
    except Member.DoesNotExist:
        return JsonResponse({"message": "User not found", "error": 30}, status=404)

    if not (team.team_leaders.contains(request.user) or request.user == team.creator):
        return JsonResponse({"message": "Not authorized", "error": 32}, status=403)

    if not (team.team_members.contains(user) or team.team_leaders.contains(user) or team.creator == user):
        return JsonResponse({"message": "User not in team", "error": 36}, status=400)
    
    team.team_members.remove(user)
    team.team_leaders.add(user)
    return JsonResponse({"message": "User has been promoted to leader!", "error": 10})

@login_required(login_url="/")
@require_http_methods(["POST"])
def demote_member(request: WSGIRequest, team_id: int, user_id: int):
    try:
        team = Team.objects.get(pk=team_id)
        user = Member.objects.get(pk=user_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)
    except Member.DoesNotExist:
        return JsonResponse({"message": "User not found", "error": 30}, status=404)

    if not (team.team_leaders.contains(request.user) or request.user == team.creator):
        return JsonResponse({"message": "Not authorized", "error": 32}, status=403)

    if not (team.team_members.contains(user) or team.team_leaders.contains(user) or team.creator == user):
        return JsonResponse({"message": "User not in team", "error": 36}, status=400)
    
    team.team_leaders.remove(user)
    team.team_members.add(user)
    return JsonResponse({"message": "User demoted to member!", "error": 10})




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

@user_passes_test(lambda u: u.is_staff)
def create_event(request):

    if request.method == "POST":

        title = request.POST.get("title")
        details = request.POST.get("details")
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        location = request.POST.get("location")
        image = request.FILES.get("image")

        Event.objects.create(
            title=title,
            details=details,
            date=date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            image=image
        )

    return redirect(request.META.get('HTTP_REFERER', '/'))

@user_passes_test(lambda u: u.is_staff)
def edit_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        try:
            event = Event.objects.get(pk=event_id)
            event.title      = request.POST.get("title", event.title)
            event.details    = request.POST.get("details", event.details)
            event.date       = request.POST.get("date", event.date)
            event.start_time = request.POST.get("start_time", event.start_time)
            event.end_time   = request.POST.get("end_time", event.end_time)
            event.location   = request.POST.get("location", event.location)
            image = request.FILES.get("image")
            if image:
                event.image = image
            event.save()
        except Event.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def delete_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        try:
            Event.objects.get(pk=event_id).delete()
        except Event.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))

@user_passes_test(lambda u: u.is_staff)
def edit_team(request):
    if request.method == "POST":
        team_id = request.POST.get("team_id")
        try:
            team             = Team.objects.get(pk=team_id)
            team.name        = request.POST.get("name", team.name)
            team.description = request.POST.get("description", team.description)

            # members
            member_ids = request.POST.getlist("member_ids")
            if member_ids:
                team.team_members.set(Member.objects.filter(id__in=member_ids))
            else:
                team.team_members.clear()

            # leaders
            leader_ids = request.POST.getlist("leader_ids")
            if leader_ids:
                team.team_leaders.set(Member.objects.filter(id__in=leader_ids))
            else:
                team.team_leaders.clear()

            team.save()
        except Team.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def admin_delete_team(request):
    if request.method == "POST":
        team_id = request.POST.get("team_id")
        try:
            Team.objects.get(pk=team_id).delete()
        except Team.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))

@user_passes_test(lambda u: u.is_staff)
def search_members(request):
    query = request.GET.get("q", "").strip()
    members = Member.objects.filter(
        first_name__icontains=query
    ) | Member.objects.filter(
        last_name__icontains=query
    ) | Member.objects.filter(
        email__icontains=query
    )
    data = [
        {"id": m.id, "name": f"{m.first_name} {m.last_name}", "email": m.email}
        for m in members[:10]
    ]
    return JsonResponse({"members": data})