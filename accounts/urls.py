from rest_framework import routers
from .views import *
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

app_name = 'Account'
router = routers.DefaultRouter()

router.register(r'employees', EmployeeViewSet)
router.register(r'employee/register', RegisterViewSet, basename='user/register')
router.register(r'recruiter/register', RecruiterRegisterViewSet, basename='recruiter/register')
urlpatterns = [
    path('api/token/', csrf_exempt(MyTokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('api/token/refresh/', csrf_exempt(MyTokenRefreshView.as_view()), name='token_refresh'),
    path('employee/login/', csrf_exempt(LoginView.as_view()), name='login'),
    path('employee/verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('employee/pdf-upload/', UploadPDFView.as_view(), name='pdf_upload'),
]

urlpatterns += router.urls