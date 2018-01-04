from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from core.models import TimeStampedModel

class Org(TimeStampedModel):
    title = models.CharField(max_length=50)
    admin = models.ForeignKey('accounts.Account', related_name="admin_orgs")
    subscription_type = models.CharField(max_length=30)
    subscription_id = models.CharField(max_length=30)
    subscription_status = models.CharField(max_length=30)
    sub_status = models.IntegerField(blank=True)

    email_domain = models.CharField(max_length=50)
    email_all = models.BooleanField(default=False)

    def update_sub_status(self):
        subscription_type = self.subscription_type
        subscription_status = self.subscription_status
        # The user identified by email
        if subscription_type == "Trial":
            if subscription_status == "Pending":
                self.sub_status = 0;
            elif subscription_status == "Active":
                self.sub_status = 1;
            elif subscription_status == "Failed":
                self.sub_status = 2;
        elif subscription_type == "Monthly":
            if subscription_status == "Active":
                self.sub_status = 3;
            elif subscription_status == "Failed":
                self.sub_status = 4;
        self.save()

    # Fields to add: size, category
    
    def __str__(self):
        return "%s" % (self.title)
    
    class Meta:
        ordering = ('title',)
        permissions = (
            ("view_org", "View org"),
            ("create_prod", "Create org product"),
            ("create_feat", "Create org feature"),
            ("create_anno", "Create org annotation"),
            ("create_quest", "Create org question"),
        )


class Expert(TimeStampedModel):
    account = models.OneToOneField('accounts.Account', on_delete=models.CASCADE)
    orgs = models.ManyToManyField('orgs.Org', related_name='experts')


    def __str__(self):
        return self.account

    class Meta:
        ordering = ('account',)

class Skill(TimeStampedModel):
    title = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    orgs = models.ManyToManyField('orgs.Org', related_name='skills')
    experts = models.ManyToManyField(Expert, related_name='skills')


    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)