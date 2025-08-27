from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ticket.views import TicketViewSet, AnswerTicketViewSet

router = DefaultRouter()
router.register('tickets', TicketViewSet, basename="tickets")
router.register('answers', AnswerTicketViewSet, basename="answers")



urlpatterns = [
    path('', include(router.urls)),
]