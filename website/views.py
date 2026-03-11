import json
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth import get_user_model

from website.context_processors import log_activity
from website.models import Event, Team, ActivityLog, Workshop, WorkshopFile
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
    events = Event.objects.all().order_by("date", "start_time")
    teams_qs = Team.objects.prefetch_related("team_members", "team_leaders").all()
    activity = ActivityLog.objects.all()[:10]
    workshops = Workshop.objects.prefetch_related("files").all()

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
            "obj": team,
            "leaders_str": leaders_str,
            "member_count": team.team_members.count(),
            "leader_count": team.team_leaders.count(),
            "leaders_json": json.dumps(leaders_list),
            "members_json": json.dumps(members_list),
        })

    workshops_json = json.dumps([
        {
            "id": w.id,
            "type": w.content_type,
            "title": w.title,
            "module": w.module,
            "desc": w.description,
            "tags": w.tags_list(),
            "version": w.version,
            "status": w.status,
            "date": w.date.isoformat(),
            "creator_id": w.creator_id,
            "creator_name": f"{w.creator.first_name} {w.creator.last_name}" if w.creator else "Unknown",
            "files": [{"id": f.id, "name": f.name, "size": f.size} for f in w.files.all()],
            "history": [],
        }
        for w in workshops
    ])

    return render(request, "admin-dashboard.html", {
        "members": members,
        "events": events,
        "teams": teams,
        "activity": activity,
        "user_count": Member.objects.count(),
        "team_count": Team.objects.count(),
        "event_count": Event.objects.filter(date__gte=date.today()).count(),
        "workshops_json": workshops_json,
        "current_user_id": request.user.id,
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
    return render(request, "student-dashboard.html", {"teams": teams, "events": Event.objects.all()})


@login_required(login_url="/")
def student_events(request: WSGIRequest):
    return render(request, "student-events.html")


@login_required(login_url="/")
def student_teams(request: WSGIRequest):
    joined_teams = []
    invited_teams = []
    for team in Team.objects.all():
        if request.user in team.team_leaders.all() or request.user in team.team_members.all() or request.user == team.creator or request.user in team.pending_members.all():
            joined_teams.append(team)
        elif request.user in team.invited_members.all():
            invited_teams.append(team)
    return render(request, "student-teams.html",
                  {"teams": Team.objects.all(), "joined_teams": joined_teams, "invited_teams": invited_teams})


@login_required(login_url="/")
def team_detail(request: WSGIRequest, team_id: int):
    team = get_object_or_404(Team, pk=team_id)
    op = False
    if request.user in team.team_leaders.all() or request.user == team.creator:
        op = True
    return render(request, "team-detail.html", {"team": team, "op": op})


@login_required(login_url="/")
def student_profile(request: WSGIRequest):
    is_admin = request.GET.get("admin") == "true"
    return render(request, "student-profile.html", {
        "is_admin": is_admin
    })


# ════════════════════════════════════════════════════════════
#  TEAM API ENDPOINTS
# ════════════════════════════════════════════════════════════

@login_required(login_url="/")
@require_http_methods(["POST"])
def create_team(request: WSGIRequest):
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()

    if not name:
        return JsonResponse({"message": "Team name is required", "error": 40}, status=400)

    team = Team(name=name, description=description)
    team.save()
    team.team_leaders.add(request.user)
    team.save()

    return JsonResponse({"message": "Team created successfully", "error": 10, "team_id": team.pk})


@login_required(login_url="/")
@require_http_methods(["DELETE"])
def delete_team(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"message": "Team not found", "error": 30}, status=404)

    if not team.team_leaders.contains(request.user):
        return JsonResponse({"message": "Not authorised", "error": 32}, status=403)

    team.delete()
    return JsonResponse({"message": "Team deleted successfully", "error": 10})


@login_required(login_url="/")
@require_http_methods(["POST"])
def join_team(request: WSGIRequest, team_id: int):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
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
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
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
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
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
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
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
            role_label = "Staff" if is_staff else "Student"
            log_activity(ActivityLog.Action.ROLE_CHANGED,
                         f"{user.first_name} {user.last_name} changed to {role_label}")
        except Member.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def delete_member(request):
    if request.method == "POST":

        email = request.POST.get("email")

        try:
            user = Member.objects.get(email=email)
            log_activity(ActivityLog.Action.USER_DELETED,
                         f"User deleted: {user.first_name} {user.last_name}")
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
        log_activity(ActivityLog.Action.EVENT_CREATED, f"Event created: {title}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def edit_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        try:
            event = Event.objects.get(pk=event_id)
            event.title = request.POST.get("title", event.title)
            event.details = request.POST.get("details", event.details)
            event.date = request.POST.get("date", event.date)
            event.start_time = request.POST.get("start_time", event.start_time)
            event.end_time = request.POST.get("end_time", event.end_time)
            event.location = request.POST.get("location", event.location)
            image = request.FILES.get("image")
            if image:
                event.image = image
            event.save()
            log_activity(ActivityLog.Action.EVENT_EDITED, f"Event edited: {event.title}")
        except Event.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def delete_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        try:
            event = Event.objects.get(pk=event_id)
            log_activity(ActivityLog.Action.EVENT_DELETED, f"Event deleted: {event.title}")
            event.delete()
        except Event.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def edit_team(request):
    if request.method == "POST":
        team_id = request.POST.get("team_id")
        try:
            team = Team.objects.get(pk=team_id)
            team.name = request.POST.get("name", team.name)
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
            log_activity(ActivityLog.Action.TEAM_EDITED, f"Team edited: {team.name}")
        except Team.DoesNotExist:
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def admin_delete_team(request):
    if request.method == "POST":
        team_id = request.POST.get("team_id")
        try:
            team = Team.objects.get(pk=team_id)
            log_activity(ActivityLog.Action.TEAM_DELETED, f"Team deleted: {team.name}")
            team.delete()
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


# ════════════════════════════════════════════════════════════
#  ADMIN — WORKSHOP CRUD
# ════════════════════════════════════════════════════════════

def _staff_required(view_fn):
    """
    Decorator for AJAX-only workshop views.
    Returns JSON 403 instead of redirecting, so fetch() gets a proper
    response rather than silently following a redirect to the login page.
    """
    from functools import wraps
    @wraps(view_fn)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)
        return view_fn(request, *args, **kwargs)

    return wrapper


@_staff_required
def create_workshop(request):
    """Create a new workshop draft."""
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"ok": False, "error": "Title is required"}, status=400)

    workshop = Workshop.objects.create(
        title=title,
        content_type=request.POST.get("type", "Document"),
        module=request.POST.get("module", "").strip(),
        description=request.POST.get("desc", "").strip(),
        tags=request.POST.get("tags", "").strip(),
        version=request.POST.get("version", "1.0").strip() or "1.0",
        status="draft",
        creator=request.user,
    )
    _attach_files(request, workshop)
    log_activity(
        ActivityLog.Action.WORKSHOP_CREATED,
        f'Workshop draft created: "{workshop.title}" by {request.user.first_name} {request.user.last_name}',
    )
    return JsonResponse({"ok": True, "id": workshop.pk})


@_staff_required
def edit_workshop(request):
    """Edit an existing workshop — only the creator may do this."""
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    workshop_id = request.POST.get("workshop_id")
    try:
        w = Workshop.objects.get(pk=workshop_id)
    except Workshop.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Not found"}, status=404)

    if w.creator_id != request.user.id:
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    old_status = w.status
    w.title = request.POST.get("title", w.title).strip() or w.title
    w.content_type = request.POST.get("type", w.content_type)
    w.module = request.POST.get("module", w.module).strip()
    w.description = request.POST.get("desc", w.description).strip()
    w.tags = request.POST.get("tags", w.tags).strip()
    w.version = request.POST.get("version", w.version).strip() or w.version
    w.status = request.POST.get("status", w.status)
    w.save()

    remove_ids = request.POST.getlist("remove_file_ids")
    if remove_ids:
        WorkshopFile.objects.filter(pk__in=remove_ids, workshop=w).delete()

    _attach_files(request, w)

    log_activity(
        ActivityLog.Action.WORKSHOP_EDITED,
        f'Workshop edited: "{w.title}" by {request.user.first_name} {request.user.last_name}',
    )
    return JsonResponse({"ok": True})


@_staff_required
def delete_workshop(request):
    """Delete a workshop — only the creator may do this."""
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    workshop_id = request.POST.get("workshop_id")
    try:
        w = Workshop.objects.get(pk=workshop_id)
    except Workshop.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Not found"}, status=404)

    if w.creator_id != request.user.id:
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    title = w.title
    w.delete()
    log_activity(
        ActivityLog.Action.WORKSHOP_DELETED,
        f'Workshop deleted: "{title}" by {request.user.first_name} {request.user.last_name}',
    )
    return JsonResponse({"ok": True})


@_staff_required
def set_workshop_status(request):
    """Bulk status change — only affects workshops owned by the requesting user."""
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    ids = request.POST.getlist("workshop_ids")
    status = request.POST.get("status")
    if status not in ("published", "draft", "archived"):
        return JsonResponse({"ok": False, "error": "Invalid status"}, status=400)

    workshops = Workshop.objects.filter(pk__in=ids, creator=request.user)
    titles = list(workshops.values_list("title", flat=True))
    updated = workshops.update(status=status)

    if updated:
        action_map = {
            "published": ActivityLog.Action.WORKSHOP_PUBLISHED,
            "archived": ActivityLog.Action.WORKSHOP_ARCHIVED,
            "draft": ActivityLog.Action.WORKSHOP_EDITED,
        }
        label = {"published": "Published", "archived": "Archived", "draft": "Moved to draft"}[status]
        log_activity(
            action_map[status],
            f'{label} {updated} workshop(s): {", ".join(titles[:3])}{"…" if len(titles) > 3 else ""}'
            f' — {request.user.first_name} {request.user.last_name}',
        )

    return JsonResponse({"ok": True, "updated": updated})


@_staff_required
def download_workshop_file(request, file_id):
    from django.http import FileResponse
    f = get_object_or_404(WorkshopFile, pk=file_id)
    return FileResponse(f.file.open(), as_attachment=True, filename=f.name)


# ── helpers ──────────────────────────────────────────────────

def _attach_files(request, workshop: Workshop):
    """Attach uploaded files to a workshop, grouped by field name → file type."""
    type_map = {
        "documents": WorkshopFile.FileType.DOCUMENT,
        "presentations": WorkshopFile.FileType.PRESENTATION,
        "videos": WorkshopFile.FileType.VIDEO,
        "resources": WorkshopFile.FileType.RESOURCE,
    }
    for field, file_type in type_map.items():
        for f in request.FILES.getlist(field):
            WorkshopFile.objects.create(workshop=workshop, file=f, file_type=file_type, name=f.name,
                                        size=f"{round(f.size / 1024, 1)} KB", )
