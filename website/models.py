from django.db import models
from accounts import models as accountModels


# Create your models here.
class Team(models.Model):
    name = models.CharField()
    description = models.TextField()
    team_leaders = models.ManyToManyField(accountModels.Member, related_name="team_leaders")
    team_members = models.ManyToManyField(accountModels.Member, related_name="team_members", blank=True)
    pending_members = models.ManyToManyField(accountModels.Member, related_name="pending_members", blank=True)
    invited_members = models.ManyToManyField(accountModels.Member, related_name="invited_members", blank=True)
    creator = models.ForeignKey(accountModels.Member, on_delete=models.CASCADE)


class Event(models.Model):
    title = models.CharField()
    details = models.TextField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    location = models.CharField()
    image = models.ImageField(default="events/events_icon.svg", upload_to="events/")


class ActivityLog(models.Model):
    class Action(models.TextChoices):
        USER_REGISTERED = 'user_registered', 'User Registered'
        USER_DELETED = 'user_deleted', 'User Deleted'
        ROLE_CHANGED = 'role_changed', 'Role Changed'
        EVENT_CREATED = 'event_created', 'Event Created'
        EVENT_EDITED = 'event_edited', 'Event Edited'
        EVENT_DELETED = 'event_deleted', 'Event Deleted'
        TEAM_CREATED = 'team_created', 'Team Created'
        TEAM_EDITED = 'team_edited', 'Team Edited'
        TEAM_DELETED = 'team_deleted', 'Team Deleted'
        MEMBER_JOINED = 'member_joined', 'Member Joined Team'
        MEMBER_LEFT = 'member_left', 'Member Left Team'
        WORKSHOP_CREATED = 'workshop_created', 'Workshop Created'
        WORKSHOP_EDITED = 'workshop_edited', 'Workshop Edited'
        WORKSHOP_DELETED = 'workshop_deleted', 'Workshop Deleted'
        WORKSHOP_PUBLISHED = 'workshop_published', 'Workshop Published'
        WORKSHOP_ARCHIVED = 'workshop_archived', 'Workshop Archived'

    action = models.CharField(max_length=50, choices=Action.choices)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} — {self.timestamp}"


# ── Workshop content ─────────────────────────────────────────

class Workshop(models.Model):
    class Status(models.TextChoices):
        PUBLISHED = 'published', 'Published'
        DRAFT = 'draft', 'Draft'
        ARCHIVED = 'archived', 'Archived'

    class ContentType(models.TextChoices):
        PRESENTATION = 'Presentation', 'Presentation'
        DOCUMENT = 'Document', 'Document'
        VIDEO = 'Video', 'Video'

    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.DOCUMENT)
    module = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    date = models.DateField(auto_now_add=True)
    creator = models.ForeignKey(
        accountModels.Member,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='workshops',
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class WorkshopFile(models.Model):
    class FileType(models.TextChoices):
        DOCUMENT = 'document', 'Document'
        PRESENTATION = 'presentation', 'Presentation'
        VIDEO = 'video', 'Video'
        RESOURCE = 'resource', 'Resource'

    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='workshops/')
    file_type = models.CharField(max_length=20, choices=FileType.choices, default=FileType.DOCUMENT)
    name = models.CharField(max_length=255, blank=True)  # auto-filled from filename
    size = models.CharField(max_length=30, blank=True)  # human-readable, filled on save

    def save(self, *args, **kwargs):
        if self.file and not self.name:
            self.name = self.file.name.split('/')[-1]
        if self.file and not self.size:
            try:
                b = self.file.size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if b < 1024:
                        self.size = f"{b:.1f} {unit}"
                        break
                    b /= 1024
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or str(self.file)
