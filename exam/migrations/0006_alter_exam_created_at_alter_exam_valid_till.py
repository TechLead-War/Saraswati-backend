# Generated by Django 4.2.13 on 2024-07-06 12:18

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0005_exam_course_name_alter_exam_valid_till'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 6, 12, 18, 58, 790866, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 20, 12, 18, 58, 791174, tzinfo=datetime.timezone.utc)),
        ),
    ]
