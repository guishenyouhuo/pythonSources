# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-08-26 15:12
from __future__ import unicode_literals

import DjangoUeditor.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20180826_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='home_display',
            field=models.BooleanField(default=False, verbose_name='首页显示'),
        ),
        migrations.AddField(
            model_name='column',
            name='nav_display',
            field=models.BooleanField(default=False, verbose_name='导航显示'),
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=DjangoUeditor.models.UEditorField(blank=True, default='', verbose_name='内容'),
        ),
    ]
