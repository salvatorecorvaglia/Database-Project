from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    personal_phone = models.CharField(null=True, max_length=255)
    home_phone = models.CharField(null=True, max_length=255)
    REQUIRED_FIELDS = ['first_name','last_name','username','password']
    USERNAME_FIELD = 'email'

    def get_username(self):
        return self.email