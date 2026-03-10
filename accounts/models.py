from django.db import models
from .auth_utils import normalize_rit_email


# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django_countries.fields import CountryField
from django.utils import timezone

class Major(models.Model):
    code = models.CharField()
    name = models.CharField()
    def __str__(self) -> str:
        return self.code + " - " + self.name

class MemberManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, date_of_birth, gender, password=None, **extra_fields):
        if not email or not first_name or not last_name or not date_of_birth or not gender:
            raise ValueError("Value is required")

        email = normalize_rit_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name,date_of_birth=date_of_birth,gender=gender, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, date_of_birth, gender, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(first_name, last_name, email, date_of_birth, gender, password=password, **extra_fields)

class Member(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField()
    last_name = models.CharField()
    email = models.EmailField(unique=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, blank=True, null=True)
    gender = models.CharField("Gender", blank=True, null=True, choices=[("M","Male"),("F","Female"),("O","Other")])
    date_of_birth = models.DateField("Date Of Birth (YYYY-MM-DD)", blank=True, null=True)
    graduation_year = models.CharField(blank=True, null=True)
    nationality = CountryField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    objects = MemberManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name","last_name","date_of_birth","gender"]

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    # def create_user(self, email, firstname, lastname, dob, gender, password=None):

    def save(self, *args, **kwargs):
        if self.email:
            self.email = normalize_rit_email(self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        major_code = self.major.code if self.major else "No Major"
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{name or 'Unnamed User'}, {major_code} | {self.email}"


class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.otp}"