from django.contrib import admin
from ticket.models import TicketModel, AnswerTicketModel
# Register your models here.

@admin.register(TicketModel)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "lastname", "email", "Company_name")
    search_fields = ("user__username", "name", "lastname", "email", "Company_name")
    list_filter = ["Company_name"]
    # inlines = [AnswerTicketInline]


@admin.register(AnswerTicketModel)
class AnswerTicketAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "subject", "created_at")
    search_fields = ("subject", "message_text", "ticket__user__username")
    list_filter = ["created_at"]