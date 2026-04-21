from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """ Custom User Model """
   
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=True)

    def __str__(self):
       return f"{self.username}"