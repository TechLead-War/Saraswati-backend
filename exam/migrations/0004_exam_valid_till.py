# Generated by Django 4.2.13 on 2024-07-06 12:10

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_user_username_alter_user_cdate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 20, 12, 10, 6, 776413, tzinfo=datetime.timezone.utc)),
        ),
    ]
