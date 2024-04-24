from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, generics
from rest_framework import  permissions
from rest_framework.decorators import action
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
from accounts.emails import send_email_with_template
from accounts.permissions import IsEmployeePermission
from .serializers import  EmployeeSerializer, LoginSerializer, MyTokenObtainPairSerializer, PDFFileSerializer, RecruiterRegisterSerializer, UserRegisterSerializer, VertifyEmailSerializer
from .models import Employee, Recruiter, User
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try: 
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            refresh = RefreshToken(request.data.get('refresh'))
            response = {
                "status": status.HTTP_200_OK,
                "message": "Refresh successful",
                "data": {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                },
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Refresh Failed",
                "data": {
                },
            } 
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
    
class RegisterViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            if not User.objects.filter(email=request.data.get('email')).exists():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    account = serializer.save()
                    send_email_with_template(serializer.data['email'])
                    return Response({
                        'status': status.HTTP_200_OK,
                        'message': 'Register successfully. Please check your email',
                        'data': serializer.data,
                    })
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'Data invalid. Please enter again',
                    'data': serializer.errors
                })
            else:
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'This account already exists',
                    'data': {}
                })
        except Exception as e:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Data invalid. Please enter again',
                'data': serializer.errors
            })

class RecruiterRegisterViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Recruiter.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RecruiterRegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = request.data.get('account')
            if not User.objects.filter(email=user['email']).exists():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    account = serializer.save()
                    send_email_with_template(user['email'])
                    serialized_user = UserRegisterSerializer(data=user)
                    return Response({
                        'status': status.HTTP_200_OK,
                        'message': 'Register successfully. Please check your email',
                        'data': user
                    })
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'Data invalid. Please enter again',
                    'data': serializer.errors
                })
            else:
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'This account already exists',
                    'data': {}
                })
        except Exception as e:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Data invalid. Please enter again',
                'data': serializer.errors
            })
        

class VerifyEmail(APIView):
    @swagger_auto_schema(
        request_body=VertifyEmailSerializer,  # Specify the serializer used for request data
        responses={
            status.HTTP_202_ACCEPTED: "Register successful!",  # Add response description
            status.HTTP_400_BAD_REQUEST: "Invalid data. Please enter again",  # Add response description
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = VertifyEmailSerializer(data=data)
            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']
                user = User.objects.get(email=email)
                if not user:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Invalid Email. Please enter again',
                        'data': serializer.errors
                    })
                if user.otp != otp:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Invalid OTP. Please enter again',
                        'data': serializer.errors
                    })
                user.is_verified = True
                user.save()
                refresh = MyTokenObtainPairSerializer.get_token(user)
                return Response({
                    'status': status.HTTP_202_ACCEPTED,
                    'message': 'Register successfully!',
                    'data': {
                        'email': user.email,
                        'refresh_token': str(refresh),
                        'access_token': str(refresh.access_token),
                        'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                        'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                    }
                })
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data. Please enter again',
                'data': serializer.errors
            })

        except Exception as e:
            print(e)
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data. Please enter again',
                'data': serializer.errors
            })
            
        
class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,  # Specify the serializer used for request data
        responses={
            status.HTTP_202_ACCEPTED: "Login successful",  # Add response description
            status.HTTP_400_BAD_REQUEST: "Invalid password",  # Add response description
            status.HTTP_406_NOT_ACCEPTABLE: "Account is not verified. Please try again",  # Add response description
        },
    )

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
            if serializer.is_valid():
                email = serializer.data['email']
                password = serializer.data['password']
                user = authenticate(request, email=email, password=password)
                if user is None:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Invalid password',
                        'data': {}
                    })
                if user.is_verified is False:
                    return Response({
                        'status': status.HTTP_406_NOT_ACCEPTABLE,
                        'message': 'Account is not verified. Please try again',
                        'data': {'email': user.email}
                    })
                serializer_token = MyTokenObtainPairSerializer.get_token(user)
                response = {
                    "status": status.HTTP_202_ACCEPTED,
                    "message": "Login successful",
                    "data": {
                        'email': user.email,
                        'refresh_token': str(serializer_token),
                        'access_token': str(serializer_token.access_token),
                        'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                        'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                    },
                }
                return Response(response, status=status.HTTP_202_ACCEPTED)
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data. Please enter again',
                'data': {}
            })
        except Exception as e:
            print(e)
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data. Please enter again',
                'data': {}
            })

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('account')
    permission_classes = [IsEmployeePermission, IsAuthenticated]
    serializer_class = EmployeeSerializer


class UploadPDFView(APIView):
    queryset = Employee.objects.select_related('account')
    permission_classes = [IsEmployeePermission, IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(
        request_body=PDFFileSerializer,
        operation_description="Upload a PDF file",
        responses={
            200: "{'url': 'https://cloudinary.com/your_url'}",
            400: "{'error': 'Invalid file format'}",
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            if 'pdf_file' not in request.FILES:
                response = {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "No PDF file uploaded",
                    "data": {},
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            pdf_file = request.FILES['pdf_file']
            if pdf_file.name == '':
                response = {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Empty filename",
                    "data": {},
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if not pdf_file.name.endswith('.pdf'):
                response = {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid file format",
                    "data": {},
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            employee = Employee.objects.get(account_id=request.user.id)
            uploaded_file = cloudinary.uploader.upload(pdf_file,folder=f'hireIT/employees/{request.user.id}', access_mode="public")
            print(uploaded_file['secure_url'])
            # return Response({'url': uploaded_file['secure_url']}, status=200)
            employee.pdf_file = uploaded_file['secure_url']
            employee.save()
            response = {
                "status": status.HTTP_200_OK,
                "message": "PDF file uploaded successfully",
                "data": {"url": uploaded_file['secure_url']},
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Upload Failed",
                "data": {},
            } 
            return Response(response, status=status.HTTP_401_UNAUTHORIZED) 