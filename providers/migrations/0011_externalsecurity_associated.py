# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-11 22:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0005_auto_20180102_1727'),
        ('providers', '0010_auto_20180110_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalsecurity',
            name='associated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='external_security_link', to='security.Security'),
        ),
    ]
