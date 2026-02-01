from django.contrib import admin

# Register your models here.
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Member


class MemberAdmin(UserAdmin):
    # add_form = CustomUserCreationForm 
    # form = CustomUserChangeForm
    model = Member
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    ]
    ordering = ["email", "first_name", "last_name", "gender","date_of_birth"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name","last_name","date_of_birth","nationality","gender","major","graduation_year")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    # list_f


admin.site.register(Member, MemberAdmin)