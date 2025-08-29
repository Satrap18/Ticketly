from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import RegisterUserView, SetTelegramIDView

router = DefaultRouter()
router.register(r'users', RegisterUserView, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('set-telegram-id/', SetTelegramIDView.as_view(), name='set_telegram_id'),

]