# Generated by Django 4.2.13 on 2024-07-21 05:03

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0024_user_exam_prefix_alter_exam_valid_till'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='NA', max_length=10),
        ),
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 4, 5, 3, 53, 208005, tzinfo=datetime.timezone.utc)),
        ),
    ]
