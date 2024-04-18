from rest_framework import routers
from .views import *
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

router = routers.DefaultRouter()

router.register(r'employee/register', RegisterViewSet, basename='user/register')
router.register(r'recruiter/register', RecruiterRegisterViewSet, basename='recruiter/register')
urlpatterns = [
    path('api/token', csrf_exempt(MyTokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/token/refresh', csrf_exempt(MyTokenRefreshView.as_view()), name='token_refresh'),
    path('employee/login/', csrf_exempt(LoginView.as_view()), name='login'),
]

urlpatterns += router.urls