# Generated by Django 4.2.13 on 2024-07-06 13:10

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0007_alter_exam_created_at_alter_exam_valid_till'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 20, 13, 10, 43, 324508, tzinfo=datetime.timezone.utc)),
        ),
    ]
