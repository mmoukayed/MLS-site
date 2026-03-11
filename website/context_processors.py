from accounts.models import Major
from django_countries import countries
from django.utils import timezone
from website.models import Event, Team, ActivityLog



def prereqData(request):
    """
    Injected into every template automatically (register in settings.py).
    Provides majors + nationalities for the signup modal in base.html,
    so no view needs to pass them manually.
    """
    return {
        "majors":        Major.objects.all().order_by("name"),
        "nationalities": list(countries),
        "now":           timezone.now(),   # handy for footer copyright year etc.
    }
def log_activity(action, message):
    ActivityLog.objects.create(action=action, message=message)