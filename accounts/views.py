import json
from datetime import timedelta

from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django_countries import countries
from django.core.handlers.wsgi import WSGIRequest

from .models import Member, EmailOTP, Major
from .emails import send_login_email
from .auth_utils import verify_magic_token, normalize_rit_email
from .validators import university_email_validator


# ─── Helper: context shared by pages that render base.html ───────
def _base_context():
    """Provides majors + nationalities needed by the signup modal in base.html."""
    return {
        "majors":       Major.objects.all().order_by("name"),
        "nationalities": list(countries),
    }


# ════════════════════════════════════════════════════════════════
#  REQUEST LOGIN  (send OTP / magic link to existing member)
# ════════════════════════════════════════════════════════════════

@require_http_methods(["POST"])
def request_login(request):
    try:
        data  = json.loads(request.body)
        email = normalize_rit_email(data.get("email", ""))

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        try:
            university_email_validator(email)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

        try:
            Member.objects.get(email=email)
        except Member.DoesNotExist:
            return JsonResponse({"error": "No account found with this email. Please sign up first."}, status=404)

        send_login_email(email)

        return JsonResponse({"message": "Login email sent! Check your inbox for the code or magic link."})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid request"}, status=400)
    except Exception:
        return JsonResponse({"error": "Something went wrong. Please try again."}, status=500)


# ════════════════════════════════════════════════════════════════
#  MAGIC LINK LOGIN
# ════════════════════════════════════════════════════════════════

def magic_login(request):
    token = request.GET.get("token")
    if not token:
        return HttpResponse("No token provided.", status=400)

    email = normalize_rit_email(verify_magic_token(token))
    if not email:
        return HttpResponse("This link is invalid or has expired. Please request a new one.", status=400)

    try:
        member = Member.objects.get(email=email)
    except Member.DoesNotExist:
        # Attempt to complete signup from session
        pending = request.session.get("pending_signup")
        if not pending or pending.get("email") != email:
            return HttpResponse("Signup session expired. Please sign up again.", status=400)

        member = Member.objects.create_user(
            email=pending["email"],
            first_name=pending["first_name"],
            last_name=pending["last_name"],
            date_of_birth=pending["dob"],
            gender=pending["gender"],
            graduation_year=pending.get("graduation_year"),
            nationality=pending.get("nationality"),
        )
        if pending.get("major"):
            try:
                member.major = Major.objects.get(pk=pending["major"])
                member.save()
            except Major.DoesNotExist:
                pass

        request.session.pop("pending_signup", None)

    # Mark all unused OTPs for this email as used (link login counts as auth)
    EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)

    login(request, member, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("/")


# ════════════════════════════════════════════════════════════════
#  OTP LOGIN  (verify 6-digit code — used by both login & signup)
# ════════════════════════════════════════════════════════════════

@require_http_methods(["POST"])
def otp_login(request):
    try:
        data  = json.loads(request.body)
        email = normalize_rit_email(data.get("email", ""))
        otp   = data.get("otp", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not email or not otp:
        return JsonResponse({"error": "Email and OTP are required"}, status=400)

    if not otp.isdigit() or len(otp) != 6:
        return JsonResponse({"error": "OTP must be 6 digits"}, status=400)

    record = EmailOTP.objects.filter(
        email=email,
        otp=otp,
        is_used=False,
        created_at__gte=timezone.now() - timedelta(minutes=5),
    ).order_by("-created_at").first()

    if not record:
        return JsonResponse({"error": "Invalid or expired code. Please try again."}, status=400)

    record.is_used = True
    record.save()

    try:
        member = Member.objects.get(email=email)
    except Member.DoesNotExist:
        # New user – pull from session
        pending = request.session.get("pending_signup")
        if not pending or pending.get("email") != email:
            return JsonResponse({"error": "Signup session expired. Please sign up again."}, status=400)

        member = Member.objects.create_user(
            email=pending["email"],
            first_name=pending["first_name"],
            last_name=pending["last_name"],
            date_of_birth=pending["dob"],
            gender=pending["gender"],
            graduation_year=pending.get("graduation_year"),
            nationality=pending.get("nationality"),
        )
        if pending.get("major"):
            try:
                member.major = Major.objects.get(pk=pending["major"])
                member.save()
            except Major.DoesNotExist:
                pass

        request.session.pop("pending_signup", None)

    login(request, member, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse({"message": "Login successful", "redirect": "/"})


# ════════════════════════════════════════════════════════════════
#  RESEND OTP
# ════════════════════════════════════════════════════════════════

@require_http_methods(["POST"])
def resend_otp(request):
    try:
        data  = json.loads(request.body)
        email = normalize_rit_email(data.get("email", ""))

        if not email:
            return JsonResponse({"error": "Email required"}, status=400)

        university_email_validator(email)

        # Rate limit: max 3 resends per minute
        recent = EmailOTP.objects.filter(
            email=email,
            created_at__gte=timezone.now() - timedelta(minutes=1),
        ).count()
        if recent >= 3:
            return JsonResponse({"error": "Too many requests. Please wait a minute and try again."}, status=429)

        # Invalidate old unused OTPs
        EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)

        send_login_email(email)
        return JsonResponse({"message": "New code sent! Check your inbox."})

    except Exception as e:
        print(e)
        return JsonResponse({"error": "Something went wrong"}, status=500)


# ════════════════════════════════════════════════════════════════
#  SIGNUP  (POST saves session + sends OTP; GET not used — modal)
# ════════════════════════════════════════════════════════════════

@require_http_methods(["POST"])
def signup(request: WSGIRequest):
    try:
        email = normalize_rit_email(request.POST.get("email", ""))
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        university_email_validator(email)

        if Member.objects.filter(email=email).exists():
            return JsonResponse({"error": "An account already exists with this email. Please log in."}, status=409)

        # Store pending data in session
        request.session["pending_signup"] = {
            "email":           email,
            "first_name":      request.POST.get("first_name", "").strip(),
            "last_name":       request.POST.get("last_name", "").strip(),
            "dob":             request.POST.get("dob", ""),
            "gender":          request.POST.get("gender", ""),
            "graduation_year": request.POST.get("graduation_year", ""),
            "nationality":     request.POST.get("nationality", ""),
            "major":           request.POST.get("field_of_study", ""),
        }
        request.session["otp_email"] = email
        request.session.modified = True

        send_login_email(email)

        return JsonResponse({
            "success": True,
            "message": "Account created! Please enter the verification code sent to your email.",
            "email":   email,
        })

    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


# ════════════════════════════════════════════════════════════════
#  PAGE VIEWS  (all render base.html so need base context)
# ════════════════════════════════════════════════════════════════

def login_page(request):
    """Standalone login page — redirects to home if already authed.
    The modal is in base.html; this just shows it pre-opened via JS."""
    if request.user.is_authenticated:
        return redirect("/")
    ctx = _base_context()
    ctx["open_login"] = True
    return render(request, "index.html", ctx)


def logout_view(request):
    logout(request)
    return redirect("/")