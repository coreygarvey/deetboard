# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-26 21:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotations', '0002_annotation_profilepic'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='annotation',
            name='role',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
