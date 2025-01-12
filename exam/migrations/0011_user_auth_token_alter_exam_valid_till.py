# Generated by Django 4.2.13 on 2024-07-06 13:58

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0010_user_last_logged_in_alter_exam_valid_till'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_token',
            field=models.CharField(max_length=36, null=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 20, 13, 58, 35, 500566, tzinfo=datetime.timezone.utc)),
        ),
    ]
