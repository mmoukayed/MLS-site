from accounts.models import Member, EmailOTP, Major
from django_countries import countries
def prereqData(request):
    return {"majors": Major.objects.all(), "nationalities": countries}
