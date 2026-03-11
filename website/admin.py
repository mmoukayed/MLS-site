from django.contrib import admin

from .models import *


class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "pk")


class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "pk", "date", "start_time", "end_time", "location")


admin.site.register(Team, TeamAdmin)
admin.site.register(Event, EventAdmin)


# ── ActivityLog ─────────────────────────────────────────────
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'message', 'timestamp')
    list_filter = ('action',)
    search_fields = ('message',)
    readonly_fields = ('action', 'message', 'timestamp')  # logs should not be editable

    def has_add_permission(self, request):
        return False  # logs are created by the app, not manually


# ── WorkshopFile inline ──────────────────────────────────────
class WorkshopFileInline(admin.TabularInline):
    model = WorkshopFile
    extra = 0
    fields = ('file', 'file_type', 'name', 'size')
    readonly_fields = ('name', 'size')  # auto-filled on save


# ── Workshop ─────────────────────────────────────────────────
@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'status', 'version', 'creator', 'date')
    list_filter = ('status', 'content_type')
    search_fields = ('title', 'module', 'tags')
    ordering = ('-date',)
    readonly_fields = ('date',)
    inlines = [WorkshopFileInline]


# ── WorkshopFile (standalone, in case you want to search files directly) ──
@admin.register(WorkshopFile)
class WorkshopFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'workshop', 'file_type', 'size')
    list_filter = ('file_type',)
    search_fields = ('name', 'workshop__title')
    readonly_fields = ('name', 'size')
