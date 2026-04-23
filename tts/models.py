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


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Tools(BaseModel):
    name = models.CharField(unique=True)

    def __str__(self):
        return f"{self.name}"


class TTSModels(BaseModel):
    name = models.CharField(unique=True)
    tool = models.ForeignKey(Tools, on_delete=models.CASCADE, related_name='models')
    model_id = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.tool}: {self.name}"