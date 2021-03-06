# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-07 07:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Chat', '0004_auto_20160605_2332'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('O', 'Online'), ('D', 'Offline')], max_length=2)),
                ('signature', models.TextField(max_length=140, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=2)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='friendrelation',
            name='u1_chat_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='friendrelation',
            name='u2_chat_num',
            field=models.IntegerField(default=0),
        ),
    ]
