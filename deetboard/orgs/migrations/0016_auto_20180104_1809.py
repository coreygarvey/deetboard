# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-04 18:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0015_auto_20180104_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='org',
            name='current_period_end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='org',
            name='current_period_start',
            field=models.DateTimeField(null=True),
        ),
    ]
