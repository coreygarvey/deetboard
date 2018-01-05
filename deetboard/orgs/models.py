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
    # paid or unpaid
    subscription_status = models.CharField(max_length=30)

    unpaid_invoice = models.CharField(max_length=40, blank=True)

    current_period_start = models.DateTimeField(null=True)
    current_period_end = models.DateTimeField(null=True)
    subscription_amount = models.DecimalField(max_digits=6, decimal_places=2, blank=True)



    # Based on update_sub_status_int(self) below
    sub_status_int = models.IntegerField(blank=True, null=True)

    email_domain = models.CharField(max_length=50)
    email_all = models.BooleanField(default=False)

    def set_subscription(self, subscription_id, subscription_type,
                                subscription_status, current_period_start,
                                current_period_end, subscription_amount):
        self.subscription_id = subscription_id
        self.subscription_type = subscription_type
        self.subscription_status = subscription_status
        
        self.current_period_start = current_period_start
        
        self.current_period_end = current_period_end
        
        self.subscription_amount = subscription_amount
        self.save()


    def update_sub_status_int(self):
        subscription_type = self.subscription_type
        subscription_status = self.subscription_status
        admin_cc_active = self.admin.cc_active
        # The user identified by email
        if subscription_type == "trial":
            if admin_cc_active == False:
                self.sub_status_int = 0;
            elif admin_cc_active == True:
                self.sub_status_int = 1;
        elif subscription_type == "monthly":
            if subscription_status == "paid":
                if admin_cc_active == False:
                    self.sub_status_int = 2;
                elif admin_cc_active == True:
                    self.sub_status_int = 3;
            if subscription_status == "unpaid":
                if admin_cc_active == False:
                    self.sub_status_int = 4;
                elif admin_cc_active == True:
                    self.sub_status_int = 5;
        self.save()



    def get_sub_clean(self):
        # The user identified by their email
        #   and role
        if self.sub_status_int == 0:
            sub_clean = "Trial - Credit Card Needed"
        elif self.sub_status_int == 1:
            sub_clean = "Trial"
        elif self.sub_status_int == 2:
            sub_clean = "Monthly - Credit Card Needed"
        elif self.sub_status_int == 3:
            sub_clean = "Monthly"
        elif self.sub_status_int == 4:
            sub_clean = "Monthly - Delinquent - CC Needed"
        elif self.sub_status_int == 5:
            sub_clean = "Monthly - Delinquent - Payment Needed"
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