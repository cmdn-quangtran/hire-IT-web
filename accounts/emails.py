from django.core.mail import send_mail
import random
from django.conf import settings
from django.template.loader import get_template
from .models import User


def send_opt_via_email(email):
    subject = 'Your account verification email'
    otp = random.randint(100000, 999999)
    message = f"Your OTP is {otp}"
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.otp = otp
    user_obj.save()

def send_email_with_template(email):
    email_from = settings.EMAIL_HOST
    subject = 'Your account verification email'
    otp = random.randint(100000, 999999)
    try:
        template = get_template('emails/verify_email.html')
        context = {'otp': otp}
        message = template.render(context)
        send_mail(subject, '', email_from, [email], html_message=message)
        user_obj = User.objects.get(email=email)
        user_obj.otp = otp
        user_obj.save()
    except Exception as e:
        print(e)