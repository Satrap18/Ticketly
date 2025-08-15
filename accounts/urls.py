from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import RegisterUserView

router = DefaultRouter()
router.register(r'users', RegisterUserView, basename='user')

urlpatterns = [
    path('', include(router.urls)),

]