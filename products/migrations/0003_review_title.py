# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-02-21 20:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='title',
            field=models.CharField(default='my review', max_length=200),
        ),
    ]
