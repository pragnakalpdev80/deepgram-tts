from django.contrib import admin

# Register your models here.
from .models import User, Tools, TTSModels

admin.site.register(User)
admin.site.register(Tools)
admin.site.register(TTSModels)