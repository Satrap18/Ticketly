from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import RegisterUserView, SetTelegramIDView, UserProfileView

router = DefaultRouter()
router.register(r'users', RegisterUserView, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('set-telegram-id/', SetTelegramIDView.as_view(), name='set_telegram_id'),
    path('profile/', UserProfileView.as_view(), name='get_profile'),

    

]