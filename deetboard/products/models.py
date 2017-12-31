from __future__ import unicode_literals

from django.db import models
from core.models import TimeStampedModel

class Product(TimeStampedModel):
    admins = models.ManyToManyField('accounts.Account', related_name='products_admin')
    title = models.CharField(max_length=50)
    description = models.TextField()
    org = models.ForeignKey('orgs.Org', related_name='products')

    image = models.FileField(upload_to='product_pics/')

    def __str__(self):
        return u'{0}'.format(self.title)
    
    class Meta:
        ordering = ('title',)
        permissions = (
            ("view_prod", "View product"),
        )


class Feature(models.Model):
    admins = models.ManyToManyField('accounts.Account', related_name='features_admin')
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    product = models.ForeignKey(Product, related_name='features')
    experts = models.ManyToManyField('accounts.Account', related_name='expert_features', blank=True)
    engagement_lists = models.ManyToManyField('feature_lists.EngagementList', related_name='features', blank=True)
    top_lists = models.ManyToManyField('feature_lists.TopList', related_name='features', blank=True)
    skills = models.ManyToManyField('orgs.Skill', related_name='features', blank=True)
    screenshots = models.ManyToManyField('screenshots.Screenshot', related_name='features', blank=True)


    def __unicode__(self):
        return u'{0}'.format(self.title)

    class Meta:
        ordering = ('title',)
        permissions = (
            ("view_feat", "View feature"),
            ("create_response", "Create Question Response"),
        )

class Link(TimeStampedModel):
    admin = models.ForeignKey('accounts.Account', related_name='links_admin')
    title = models.CharField(max_length=50)
    description = models.TextField()
    url = models.URLField()
    feature = models.ForeignKey(Feature, related_name='links')

    class Meta:
        ordering = ('title',)