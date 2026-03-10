from django.db import models
from accounts import models as accountModels

# Create your models here.
class Team(models.Model):
    name = models.CharField()
    description = models.TextField()
    team_leaders = models.ManyToManyField(accountModels.Member, related_name="team_leaders")
    team_members = models.ManyToManyField(accountModels.Member,related_name="team_members", blank=True)
    pending_members = models.ManyToManyField(accountModels.Member,related_name="pending_members", blank=True) 
    invited_members = models.ManyToManyField(accountModels.Member,related_name="invited_members", blank=True) 
    creator = models.ForeignKey(accountModels.Member, on_delete=models.CASCADE)
class Event(models.Model):
    title = models.CharField()
    details = models.TextField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    location = models.CharField()
    image = models.ImageField(default="uploaded_media/events/events_icon.svg", upload_to="uploaded_media/events")
    registration_link = models.URLField()
    new_tab = models.BooleanField("Open registration link in new tab?", default=True)
