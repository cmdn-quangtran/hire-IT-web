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
    path('employee/deactive/', DeactivePDFView.as_view(), name='deactive_pdf'),
    path('employee/verify-cv/', ExtractCVCreateView.as_view(), name='verify-job'),
    path('employee/find-job/', ExtractCVView.as_view(), name='extract_cv'),
    path('user/get-information/', GetInformation.as_view(), name='get-infomation'),
    path('user/upload-employee-profile/', UpdateEmployeeProfile.as_view(), name='upload_profile'),
    path('user/upload-recruiter-profile/', UpdateRecruiterProfile.as_view(), name='upload_profile'),
    path('employee/get-active/', GetActiveCVView.as_view(), name='get_active_cv'),
    path('employee/get-all-jobs/', JobRequirementListAPIView.as_view(), name='get_all_jobs'),


    path('recruiter/get-all-candidates/', GetAllCandidateListAPIView.as_view(), name='get_all_candidates'),
    path('recruiter/get-all-jobs-owner/', JobOwnerView.as_view(), name='get_all_candidates'),
    path('recruiter/upload-job/', UploadJobView.as_view(), name='upload_and_extract_cv'),
]

urlpatterns += router.urls
