# Generated by Django 4.2.13 on 2024-07-18 00:28

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0017_alter_exam_valid_till'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentresponse',
            name='question_id',
        ),
        migrations.RemoveField(
            model_name='studentresponse',
            name='student_id',
        ),
        migrations.AlterField(
            model_name='exam',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 1, 0, 28, 47, 449087, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='Questions',
        ),
        migrations.DeleteModel(
            name='StudentResponse',
        ),
    ]
