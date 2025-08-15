from django.contrib import admin
from accounts.models import CustomUserModel, ProfileUserModel
# Register your models here.

admin.site.register(CustomUserModel)
admin.site.register(ProfileUserModel)