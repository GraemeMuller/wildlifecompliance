# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-09-28 06:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        #('disturbance', '0004_auto_20180928_1350'),
        ('disturbance', '0006_auto_20180928_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposalrequirement',
            name='copied_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='disturbance.ProposalRequirement'),
        ),
        migrations.AddField(
            model_name='proposalrequirement',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        # migrations.AlterField(
        #     model_name='proposaltype',
        #     name='name',
        #     field=models.CharField(choices=[('Disturbance', 'Disturbance'), ('Apiary', 'Apiary')], default='Disturbance', max_length=24, verbose_name='Application name (eg. Disturbance, Apiary)'),
        # ),
    ]
