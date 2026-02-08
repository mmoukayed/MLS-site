from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import EmailOTP
from .auth_utils import generate_magic_token
import random


def send_login_email(email):
    token = generate_magic_token(email)
    magic_link = f"{settings.SITE_URL}/auth/magic-login/?token={token}"

    otp = str(random.randint(100000, 999999))

    EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)
    EmailOTP.objects.create(email=email, otp=otp)

    subject = "Your Login Code for Student Portal"

    text_content = f"""
Student Portal Login

Click to log in instantly:
{magic_link}

Or enter this code: {otp}

Valid for 5 minutes.
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                    <tr>
                        <td style="padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Student Portal Login</h1>
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px;">Choose your login method</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="background-color: #007bff; border-radius: 4px; text-align: center; padding: 15px;">
                                        <a href="{magic_link}" style="color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; display: block;">Click to Login</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px;">Or enter this code:</p>
                            <div style="background-color: #f8f9fa; border: 2px dashed #007bff; border-radius: 4px; padding: 15px; margin: 0 0 20px 0;">
                                <span style="font-size: 32px; font-weight: bold; color: #007bff; letter-spacing: 5px;">{otp}</span>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 30px 40px 30px; text-align: center;">
                            <p style="margin: 0; color: #999999; font-size: 12px;">Valid for 5 minutes. Never share this with anyone.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)