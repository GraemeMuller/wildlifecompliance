# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-12-07 07:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0104_auto_20181207_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='wildlifelicence',
            name='licence_type',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='wildlifecompliance.WildlifeLicenceActivity'),
        ),
    ]
