from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ticket.views import TicketViews

router = DefaultRouter()
router.register('ticket', TicketViews)

urlpatterns = [
    path('', include(router.urls)),
]