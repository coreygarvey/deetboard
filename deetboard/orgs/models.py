from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from core.models import TimeStampedModel

class Org(TimeStampedModel):
    title = models.CharField(max_length=50)
    admin = models.ForeignKey('accounts.Account', related_name="admin_orgs")
    
    subscription_id = models.CharField(max_length=30)
    # trial or monthly
    subscription_type = models.CharField(max_length=30)
    # active, inactive, or failed (CC not working)
    subscription_status = models.CharField(max_length=30)
    # Based on update_sub_status_int(self) below
    sub_status_int = models.IntegerField(blank=True, null=True)

    email_domain = models.CharField(max_length=50)
    email_all = models.BooleanField(default=False)

    def set_subscription(self, stripe_id, stype, sstatus):
        self.subscription_id = stripe_id
        self.subscription_type = stype
        self.subscription_status = sstatus
        self.save()


    def update_sub_status_int(self):
        subscription_type = self.subscription_type
        subscription_status = self.subscription_status
        # The user identified by email
        if subscription_type == "trial":
            if subscription_status == "inactive":
                self.sub_status_int = 0;
            elif subscription_status == "active":
                self.sub_status_int = 1;
            elif subscription_status == "failed":
                self.sub_status_int = 2;
        elif subscription_type == "monthly":
            if subscription_status == "inactive":
                self.sub_status_int = 3;
            elif subscription_status == "active":
                self.sub_status_int = 4;
        self.save()



    def get_sub_clean(self):
        # The user identified by their email
        #   and role
        if self.sub_status_int == 0:
            sub_clean = "Inctive Trial - Input Credit Card"
        elif self.sub_status_int == 1:
            sub_clean = "Active Trial"
        return sub_clean
        

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