from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django_countries.fields import CountryField
from django.utils import timezone

class Majors(models.Model):
    code = models.CharField()
    name = models.CharField()

class MemberManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, date_of_birth, gender, password=None, **extra_fields):
        if not email or not first_name or not last_name or not date_of_birth or not gender:
            raise ValueError("Value is required")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name,date_of_birth=date_of_birth,gender=gender, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, first_name, last_name, email, date_of_birth, gender, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(first_name, last_name, email, date_of_birth, gender, password, **extra_fields)

class Member(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField()
    last_name = models.CharField()
    email = models.EmailField(unique=True)
    major = models.ForeignKey(Majors, on_delete=models.CASCADE, blank=True, null=True)
    gender = models.CharField("Gender (M/F)", choices=[("M","Male"),("F","Female")],default="M")
    date_of_birth = models.DateField("Date Of Birth (YYYY-MM-DD)")
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


    def __str__(self):
        return self.email
    