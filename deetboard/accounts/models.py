from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.core.mail import send_mail
from core.models import TimeStampedModel
from django.template.loader import render_to_string
import os

class AccountManager(BaseUserManager):
	def create_user(self, email, username, role, first_name, last_name, password=None):
		"""
		Creates and saves a User with the given org, email,
		role, and password.
		"""
		if not email:
			msg = "Users must have an email address"
			raise ValueError(msg)

		if not role:
			msg = "Users must have a role"
			raise ValueError(msg)

		user = self.model(
			email=AccountManager.normalize_email(email),
			username=username,
			role=role,
			first_name=first_name,
			last_name=last_name,
		)

		user.set_password(password)
		user.save(using=self._db)
		
		return user

	def create_superuser(self, email, username, role, first_name, last_name, password):
		"""
		Creates and saves a superuser with the given
		org, email, role and password
		"""
		user = self.create_user(email, 
			password=password,
			username=username,
			role = role,
			first_name=first_name,
			last_name=last_name,
		)

		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user



class Account(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)

    date_joined = models.DateTimeField(auto_now_add=True)
    orgs = models.ManyToManyField('orgs.Org', related_name='accounts')

    primary_org = models.ForeignKey('orgs.Org', on_delete=models.CASCADE, null=True, related_name='primary_accounts')


    email = models.EmailField(
    	verbose_name="email address",
    	max_length=255,
    	unique=True,
    	db_index=True,
    )
    role = models.CharField(max_length=50, blank=True, default='')
    first_name = models.CharField(max_length=30, default='')
    last_name = models.CharField(max_length=30, default='')
    notifs = models.BooleanField(default=False)
    features_following = models.ManyToManyField('products.Feature', related_name='followers')

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    profile_pic = models.FileField(upload_to='profile_pics/')

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role', 'first_name', 'last_name']

    def get_full_name(self):
    	# The user identified by their email
    	#	and role
    	return "%s %s" % (self.first_name, self.last_name)

    def get_full_name_role(self):
    	# The user identified by their email
    	#	and role
    	return "%s %s - %s" % (self.first_name, self.last_name, self.role)

    def get_short_name(self):
    	# The user identified by email
    	return self.email

    @property
    def filename(self):
    	return os.path.basename(self.profile_pic.name)

    def email_user(self, subject, message, from_email=None, html_message=None):
		"""
		Sends an email to this User.
		"""
		email = self.email
		send_mail(subject, message, from_email, [self.email], 
					fail_silently=True, html_message=html_message)
		print "after send"

    def __unicode__(self):
    	return self.email

	

    class Meta:
        ordering = ('email',)
