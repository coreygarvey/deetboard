# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-23 09:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_auto_20170722_1405'),
    ]

    operations = [
        migrations.RenameField(
            model_name='response',
            old_name='test',
            new_name='text',
        ),
    ]
