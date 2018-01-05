from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def mailer(subject, message, from_email=None, to_email=None, html_message=None):
		"""
		Sends an email to this User.
		"""
		print "to email: "
		print to_email
		send_mail(subject, message, from_email, [to_email], fail_silently=True, html_message=html_message)
		print "after send"

from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def add(x, y):
    print "ADD"
    print x
    print y
    return x + y