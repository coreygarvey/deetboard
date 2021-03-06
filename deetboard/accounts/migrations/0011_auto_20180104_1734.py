# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-04 17:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_account_stripe_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='cc_email',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='account',
            name='cc_last_four',
            field=models.IntegerField(blank=True, default=1234),
            preserve_default=False,
        ),
    ]
