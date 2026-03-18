from django.conf import settings
from django.core.mail import EmailMessage


def send_text_email(to_email, subject, text_body, file_path = None):
    try:
        email = EmailMessage(subject, text_body, settings.EMAIL_HOST_USER, [to_email.strip()])
        if file_path:
            email.attach_file(file_path)
        email.send()
        return True
    except:
        return False

def send_html_email(to_email, subject, html_body, file_path = None):
    try:
        email = EmailMessage(subject, html_body, settings.EMAIL_HOST_USER, [to_email.strip()])
        email.content_subtype = 'html'
        if file_path:
            email.attach_file(file_path)
        email.send()
        return True
    except:
        return False

def send_file_buffer_email(to_email, subject, html_body, file_buffer, file_name):
    try:
        email = EmailMessage(subject, html_body, settings.EMAIL_HOST_USER, [to_email.strip()])
        email.content_subtype = 'html'
        if file_buffer and file_name:
            email.attach(file_name, file_buffer.read())
            email.send()
            return True
        else:
            return False
    except:
        return False
