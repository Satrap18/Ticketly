from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class CustomUserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    tel_username = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.telegram_id}"

def profile_img(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class ProfileUserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=profile_img, null=True, blank=True)
    bio = models.CharField(max_length=120)
    date_of_birth = models.DateField(blank=True, null=True)

    GENDER_CHOICES = (
        ('NotSet', 'NotSet'),
        ('Man', 'Man'),
        ('Woman', 'Woman'),
    )
    gender = models.CharField(choices=GENDER_CHOICES, default='NotSet', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
