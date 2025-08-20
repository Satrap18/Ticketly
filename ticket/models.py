from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Tikcet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    email = models.EmailField()
    Company_name = models.CharField(max_length=25)
    date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField()


    def __str__(self):
        return f"{self.user.username} - {self.name} {self.lastname}"