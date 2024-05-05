from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, generics
from rest_framework import  permissions
from rest_framework.decorators import action
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
from accounts.emails import send_email_with_template
from accounts.permissions import IsEmployeePermission, IsRecruiterPermission
from accounts.utils import extract_location, extract_phone_number, extract_skills, extract_text_from_pdf
from .serializers import  EmployeeSerializer, ExtractCVCreateSerializer, LoginSerializer, MyTokenObtainPairSerializer, PDFFileSerializer, RecruiterRegisterSerializer, RecruiterSerializer, UserRegisterSerializer, VertifyEmailSerializer
from .models import Employee, ExtractCV, Recruiter, User
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView

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
            if ExtractCV.objects.filter(employee=employee).exists():
                extract_cv = ExtractCV.objects.get(employee=employee)
                extract_cv.active = False
                extract_cv.save()
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
        
class ExtractCVView(GenericAPIView):
    permission_classes = [IsEmployeePermission, IsAuthenticated]
    serializer_class = EmployeeSerializer
    @swagger_auto_schema(
        operation_description="A custom description for the ExtractCVView",
        responses= {
            status.HTTP_200_OK: "Extract successful",  # Add response description
            status.HTTP_401_UNAUTHORIZED: "Turned on Failed",  # Add response description
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            employee = Employee.objects.get(account_id = user_id)
            text = extract_text_from_pdf(employee.pdf_file)
            location = extract_location(text)
            phone_numbers = extract_phone_number(text)
            phone_number = phone_numbers[0] if phone_numbers else None
            skills = extract_skills(text)
            response = {
                "status": status.HTTP_200_OK,
                "message": "Extract sucessfully.",
                "data": {
                    'location': location,
                    'phone_number': phone_number,
                    'skills': skills 
                },
            } 
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Turned on Failed",
                "data": {},
            } 
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

class ExtractCVCreateView(generics.GenericAPIView):
    permission_classes = [IsEmployeePermission, IsAuthenticated]
    serializer_class = ExtractCVCreateSerializer
    @swagger_auto_schema(
        operation_description="A custom description for the ExtractCVCreateView",
        request_body=ExtractCVCreateSerializer,
        responses= {
            status.HTTP_200_OK: "Turned on successfully",  # Add response description
            status.HTTP_401_UNAUTHORIZED: "Turned on Failed",  # Add response description
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user_id = request.user.id
            employee = Employee.objects.get(account_id=user_id)

            data = serializer.validated_data
            location = data.get('location')
            phone_number = data.get('phone_number')
            skills = data.get('skills')

            if ExtractCV.objects.filter(employee=employee).exists():
                extract_cv = ExtractCV.objects.get(employee=employee)
                extract_cv.phone_number = phone_number
                extract_cv.location = location
                extract_cv.skills = skills
                extract_cv.active = True
                extract_cv.save()
            else:
                extract_cv = ExtractCV.objects.create(
                    employee=employee,
                    phone_number=phone_number,
                    location=location,
                    skills=skills
                )

            response = {
                "status": status.HTTP_200_OK,
                "message": "Turned on successfully.",
                "data": {
                    'location': location,
                    'phone_number': phone_number,
                    'skills': skills 
                },
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Turned on Failed",
                "data": {},
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
class GetInformation(generics.GenericAPIView):
    serializer_class_map = {
        'GET': {
            'employee': EmployeeSerializer,
            'recruiter': RecruiterSerializer,
        }
    }
    queryset_map = {
        'employee': Employee.objects.all(),
        'recruiter': Recruiter.objects.all(),
    }

    permission_classes_map = {
        'GET': {
            'employee': [IsAuthenticated, IsEmployeePermission],
            'recruiter': [IsAuthenticated, IsRecruiterPermission],
        }
    }

    def get_permissions(self):
        user_type = 'employee' if self.request.user.role == 1 else 'recruiter'
        permission_classes = self.permission_classes_map.get(self.request.method, {}).get(user_type, [])
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        user_type = 'employee' if self.request.user.role == 1 else 'recruiter'
        return self.serializer_class_map.get(self.request.method, {}).get(user_type)

    def get(self, request, *args, **kwargs):
        try:
            user_type = 'employee' if request.user.role == 1 else 'recruiter'
            model = Employee if request.user.role == 1 else Recruiter
            queryset = self.queryset_map[user_type]
            obj = get_object_or_404(queryset, account_id=request.user.id)
            serializer_class = self.serializer_class_map['GET'][user_type]
            serializer = serializer_class(instance=obj)
            response = {
                "status": status.HTTP_200_OK,
                "message": "Successfully",
                "data": serializer.data,
            } 
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Get Information Failed",
                "data": {},
            } 
            return Response(response, status=status.HTTP_401_UNAUTHORIZED) 