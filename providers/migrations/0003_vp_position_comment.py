# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-02 19:28
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0002_remove_vp_position_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='vp_position',
            name='comment',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
    ]
