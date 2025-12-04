from django.core.mail import send_mail
from django.conf import settings
import uuid

def forget_password_mail(email,token,name):
    subject = 'Forget Password Link'
    message = f""" 
        Hi {name},

        There was a request to change your password!

        If you did not make this request then please ignore this email.

        Otherwise, please click this link to change your password:  http://127.0.0.1:8000/Change_Password/{token}"""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    result=send_mail(subject,message,email_from,recipient_list)

    if result==1:

      return True
    else:
       return False


def forget_password_mail_admin(email,token):
    subject = 'Forget Password Link'
    message = f""" 
        Respected Admin,

        There was a request to change your password!

        If you did not make this request then please ignore this email.

        Otherwise, please click this link to change your password:  http://127.0.0.1:8000/Change_Password_Admin/{token}"""
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    result=send_mail(subject,message,email_from,recipient_list)
    if result==1:

      return True
    else:
       return False