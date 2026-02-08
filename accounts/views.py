import json
from datetime import timedelta

from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Member, EmailOTP
from .emails import send_login_email
from .auth_utils import verify_magic_token
from .validators import university_email_validator


@require_http_methods(["POST"])
def request_login(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        try:
            member = Member.objects.get(email=email)
        except Member.DoesNotExist:
            return JsonResponse({"error": "No account found with this email"}, status=400)

        send_login_email(email)

        return JsonResponse({
            "message": "Login email sent! Check your inbox."
        })

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception:
        return JsonResponse({"error": "Something went wrong"}, status=500)


def magic_login(request):
    token = request.GET.get("token")

    if not token:
        return HttpResponse("No token provided", status=400)

    email = verify_magic_token(token)
    if not email:
        return HttpResponse("Invalid or expired link", status=400)

    try:
        member = Member.objects.get(email=email)
    except Member.DoesNotExist:
        data = request.session.get("pending_signup")

        if not data or data.get("email") != email:
            return HttpResponse("Signup session expired or invalid", status=400)

        # Create new member
        member = Member.objects.create_user(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["dob"],
            gender=data["gender"],
            graduation_year=data.get("graduation_year"),
            nationality=data.get("nationality"),
        )

        # Clear the pending signup from session
        request.session.pop("pending_signup", None)

        # Mark all OTPs as used
    EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)

    login(request, member)
    return redirect("/")



@require_http_methods(["POST"])
def otp_login(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        otp = data.get("otp")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not email or not otp:
        return JsonResponse({"error": "Email and OTP required"}, status=400)

    if not otp.isdigit() or len(otp) != 6:
        return JsonResponse({"error": "OTP must be 6 digits"}, status=400)

    record = EmailOTP.objects.filter(
        email=email,
        otp=otp,
        is_used=False,
        created_at__gte=timezone.now() - timedelta(minutes=5)
    ).order_by("-created_at").first()

    if not record:
        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

    record.is_used = True
    record.save()
    try:
        member = Member.objects.get(email=email)
    except Member.DoesNotExist:
        # New user - get signup data from session
        data = request.session.get("pending_signup")

        if not data or data.get("email") != email:
            return JsonResponse({"error": "Signup session expired or invalid"}, status=400)

        # Create new member
        member = Member.objects.create_user(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            date_of_birth=data["dob"],
            gender=data["gender"],
            graduation_year=data.get("graduation_year"),
            nationality=data.get("nationality"),
        )

        # Clear the pending signup from session
        request.session.pop("pending_signup", None)

    login(request, member)

    return JsonResponse({
        "message": "Login successful",
        "redirect": "/"
    })


@require_http_methods(["POST"])
def resend_otp(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"error": "Email required"}, status=400)

        university_email_validator(email)

        recent = EmailOTP.objects.filter(
            email=email,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).count()

        if recent >= 3:
            return JsonResponse(
                {"error": "Too many requests. Try again later."},
                status=429
            )

        EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)

        send_login_email(email)

        return JsonResponse({"message": "New OTP sent"})

    except Exception as e:
        return JsonResponse({"error": "Something went wrong"}, status=500)



def login_page(request):
    """Render login page"""
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "accounts/login.html")


def otp_page(request):
    # Try to get email from GET parameter first, then from session
    email = request.GET.get("email", "")

    if not email:
        email = request.session.get("otp_email", "")

    if not email:
        # No email found - redirect back to login/signup
        return redirect("/auth/login/")

    return render(request, "accounts/otp.html", {"email": email})


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            university_email_validator(email)

            if Member.objects.filter(email=email).exists():
                return render(request, "accounts/signup.html", {
                    "error": "Account already exists"
                })

            request.session["pending_signup"] = {
                "email": email,
                "first_name": request.POST["first_name"],
                "last_name": request.POST["last_name"],
                "dob": request.POST["dob"],
                "gender": request.POST["gender"],
                "graduation_year": request.POST.get("graduation_year"),
                "nationality": request.POST.get("nationality"),
            }

            request.session["otp_email"] = email
            request.session.modified = True
            send_login_email(email)
            return redirect(f"/auth/otp/?email={email}")

        except Exception as e:
            return render(request, "accounts/signup.html", {
                "error": str(e)
            })

    return render(request, "accounts/signup.html")



def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("/")
