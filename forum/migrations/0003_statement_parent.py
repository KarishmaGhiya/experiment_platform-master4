# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-17 16:37
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_auto_20160616_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='statement',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='forum.Statement'),
        ),
    ]