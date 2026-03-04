from django.contrib import admin

from .models import *
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "pk")

class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "pk", "date", "start_time", "end_time", "location")

admin.site.register(Team, TeamAdmin)
admin.site.register(Event, EventAdmin)