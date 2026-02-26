from django.db import models
from accounts import models as accountModels

# Create your models here.
class Team(models.Model):
    name = models.CharField()
    description = models.TextField()
    team_leaders = models.ManyToManyField(accountModels.Member, related_name="team_leaders")
    team_members = models.ManyToManyField(accountModels.Member,related_name="team_members")
    pending_members = models.ManyToManyField(accountModels.Member,related_name="pending_members") 