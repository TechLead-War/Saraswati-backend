# Generated by Django 4.2.13 on 2024-07-17 14:14

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0014_alter_exam_valid_till_alter_user_created_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='marks',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 31, 14, 14, 37, 268873, tzinfo=datetime.timezone.utc)),
        ),
    ]
