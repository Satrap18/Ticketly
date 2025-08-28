from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class TicketModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    name = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    email = models.EmailField()
    Company_name = models.CharField(max_length=25)
    date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField()


    def __str__(self):
        return f"{self.user.username} - {self.name} {self.lastname}"

class AnswerTicketModel(models.Model):
    ticket = models.ForeignKey(TicketModel, on_delete=models.CASCADE, related_name="answers")
    subject = models.CharField(max_length=50)
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.message_text} to {self.ticket}"