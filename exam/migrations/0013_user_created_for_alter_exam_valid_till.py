# Generated by Django 4.2.13 on 2024-07-12 15:35

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0012_alter_exam_valid_till_alter_user_university_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='created_for',
            field=models.CharField(max_length=36, null=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 26, 15, 35, 1, 172793, tzinfo=datetime.timezone.utc)),
        ),
    ]
