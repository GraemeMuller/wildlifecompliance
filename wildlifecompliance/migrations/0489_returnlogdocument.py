# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-07-13 04:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wildlifecompliance.components.returns.models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0488_auto_20200713_0738'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnLogDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('uploaded_date', models.DateTimeField(auto_now_add=True)),
                ('_file', models.FileField(upload_to=wildlifecompliance.components.returns.models.update_returns_comms_log_filename)),
                ('log_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='wildlifecompliance.ReturnLogEntry')),
            ],
        ),
    ]
