# Generated by Django 4.2.13 on 2024-07-17 15:31

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0016_user_reset_count_alter_exam_valid_till'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 31, 15, 31, 14, 92364, tzinfo=datetime.timezone.utc)),
        ),
    ]
