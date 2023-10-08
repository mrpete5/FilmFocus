from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Sends password reset request link to user object
def send_email(request, user):
    try:
        # generate token and uidb64
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct the full URL including the domain
        reset_url = reverse("password_reset_confirm", args=[uidb64, token])
        domain = request.get_host()
        reset_url = f"http://{domain}{reset_url}"

        # Send email
        send_mail(
            from_email="filmfocus@filmfocus.com",
            recipient_list=[user.email],
            subject="FilmFocus Password Reset Request",
            message=f"Click the link to reset your password: {reset_url} ",
        )
    except Exception as e:
        print("Password Reset Error:", e)

# Change Password given a user object and plaintext string
def change_password(userIn, passIn):
    userIn.set_password(passIn)
    userIn.save()

# Checks passwords for errors
def confirm_password(pass1, pass2):
    if pass1 != pass2:
        raise Exception("Passwords do not match")
    if len(pass1) < 8:
        raise Exception("Password must be at least 8 characters long")
    