from django.shortcuts import render
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
# from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from website import models
from accounts import models as accountModels
import json

# Create your views here.
@csrf_exempt
def home(request):
    print(type(request))
    return render(request, "index.html")

@csrf_exempt
def teams(request):
    if request.method == 'GET':
        return render(request, "teams.html")
    else:
        return HttpResponse(request.method + "",status=405)


@csrf_exempt
def create_team(request: WSGIRequest):
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({"message": "Not Logged In","error":20}),status=401)
    if request.method == "POST":
        team = models.Team(name=request.POST.get("name"),description=request.POST.get("description"))
        team.save()
        team.team_leaders.add(request.user)
        team.save()
        return HttpResponse(json.dumps({"message":"Team Created Successfully", "error":10, "team_id": team.pk}))
    else:
        return HttpResponse(str(request.method) + "",status=405)


@csrf_exempt
def delete_team(request: WSGIRequest, team_id: int):
    if request.method == "DELETE":
        team = models.Team.objects.get(id=team_id)
        if team is not None:
            if not request.user.is_authenticated:
                return HttpResponse(json.dumps({"message": "Not Logged In","error":20}))
            elif request.user not in team.team_leaders:
                return HttpResponse(json.dumps({"message": "Not Team Leader","error":32}))
            team.delete()
            return HttpResponse(json.dumps({"message": "Team Deleted Successfully","error":10}))
        else:
            return HttpResponse(json.dumps({"message": "Team Not Found","error":30}))
            # team.save()
    else:
        return HttpResponse(str(request.method) + "",status=405)

@csrf_exempt
def join_team(request: WSGIRequest, team_id: int):
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({"message": "Not Logged In","error":20}))
    try:
        team = models.Team.objects.get(id=team_id)
        if team.team_members.contains(request.user) or team.team_leaders.contains(request.user):
            return HttpResponse(json.dumps({"message": "Member Already In Team","error":33})) 
        team.pending_members.add(request.user)
        # TODO: send invite request to team LEADERS
        team.save()
        return HttpResponse(json.dumps({"message": "Invite Sent Successfully","error":10}))
    except: 
        return HttpResponse(json.dumps({"message": "Team Not Found","error":30}))
@csrf_exempt
def accept_invite_request(request: WSGIRequest, team_id: int, user_id: int):
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({"message": "Not Logged In","error":20}))
    try:
        team = models.Team.objects.get(id=team_id)
        if not team.team_leaders.contains(request.user):
            return HttpResponse(json.dumps({"message": "Not Authorized","error":32}))
        try:
            requested_member = accountModels.Member.objects.get(pk=user_id)
            if not team.pending_members.contains(requested_member):
                return HttpResponse(json.dumps({"message": "Member Did Not Request To Join Team","error":34}))
            if team.team_members.contains(requested_member):
                return HttpResponse(json.dumps({"message": "Member Already In Team","error":33}))
            
            team.team_members.add(requested_member)
            team.pending_members.remove(requested_member)

            team.save()
            return HttpResponse(json.dumps({"message": "Member Added To Team Successfully","error":10}))
        except:
            return HttpResponse(json.dumps({"message": "Member Not Found","error":50}))
    except:
        return HttpResponse(json.dumps({"message": "Team Not Found","error":30}))
    
@csrf_exempt
def reject_invite_request(request: WSGIRequest, team_id: int, user_id: int):
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({"message": "Not Logged In","error":20}))
    try:
        team = models.Team.objects.get(id=team_id)
        if not team.team_leaders.contains(request.user):
            return HttpResponse(json.dumps({"message": "Not Authorized","error":32}))
        try:
            requested_member = accountModels.Member.objects.get(pk=user_id)
            if not team.pending_members.contains(requested_member):
                return HttpResponse(json.dumps({"message": "Member Did Not Request To Join Team","error":34}))
            
            team.pending_members.remove(requested_member)
            team.save()

            return HttpResponse(json.dumps({"message": "Invite Rejected","error":10}))
        except:
            return HttpResponse(json.dumps({"message": "Member Not Found","error":50}))
    except:
        return HttpResponse(json.dumps({"message": "Team Not Found","error":30}))
    
@csrf_exempt
def leave_team(request: WSGIRequest, team_id: int):
    if not request.user.is_authenticated:
        return HttpResponse(json.dumps({"message": "Not Logged In","error":20}))
    
    try:
        team = models.Team.objects.get(id=team_id)
        team.team_members.remove(request.user)
        # TODO: send invite request to team LEADERS
        team.save()
        return HttpResponse(json.dumps({"message": "Left Team Successfully","error":10}))
    except:
        return HttpResponse(json.dumps({"message": "Team Not Found","error":30}))
