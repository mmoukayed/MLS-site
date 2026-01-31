from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
class Majors(models.Model):
    code = models.CharField()
    name = models.CharField()

class CustomUser(AbstractUser):
    first_name = models.CharField()
    last_name = models.CharField()
    major = models.ForeignKey(Majors, on_delete=models.CASCADE)
    gender = models.CharField(choices=[("M","Male"),("F","Female")])
    date_of_birth = models.DateField()
    year_of_graduation = models.CharField()
    nationality = CountryField()
    # add additional fields in here

    def __str__(self):
        return self.username