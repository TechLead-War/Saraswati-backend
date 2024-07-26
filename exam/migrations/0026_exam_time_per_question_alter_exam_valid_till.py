# Generated by Django 4.2.13 on 2024-07-21 14:11

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0025_user_username_alter_exam_valid_till'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='time_per_question',
            field=models.IntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 4, 14, 11, 24, 470517, tzinfo=datetime.timezone.utc)),
        ),
    ]