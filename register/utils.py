import random
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import OneTimePassword

User = get_user_model()   # ✅ this ensures it always uses register.User


def generateOtp():
    return "".join(str(random.randint(1, 9)) for _ in range(6))


def send_otp_via_email(email):
    subject = "Your One Time Password (OTP) for Email Verification"
    otp_code = generateOtp()
    print(otp_code)
    
    user = User.objects.get(email=email)   # ✅ now safe
    current_site = "myAuth.com"
    
    email_body = (
        f"Hi {user.first_name}, thanks for signing up on {current_site}. "
        f"Please verify your email with the one time passcode: {otp_code}"
    )
    
    from_email = settings.DEFAULT_FROM_EMAIL

    OneTimePassword.objects.create(user=user, code=otp_code)

    send_email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=from_email,
        to=[email]
    )
    send_email.send(fail_silently=True)


def send_normal_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()




