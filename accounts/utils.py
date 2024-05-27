
from django.core.mail import EmailMessage




def send_normal_email(data):

    message = data.get('email_body', '')
    subject = data.get('email_subject', '')
    receiver = data.get('to_email', '')
    from_email = data.get('from_email', '')
    # Now you can use these variables as needed

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=[receiver],
    )
    email.send()


