# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-22 15:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0003_auto_20160622_1513'),
        ('waiting_room', '0004_waitroom_numwait'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waituser',
            name='worker_id',
        ),
        migrations.AddField(
            model_name='waituser',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='experiment.ExpUser'),
            preserve_default=False,
        ),
    ]