# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-15 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optimized', '0004_auto_20160715_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='optimizednotoptimized',
            name='field_name',
            field=models.CharField(default='image1', max_length=100),
            preserve_default=False,
        ),
    ]
