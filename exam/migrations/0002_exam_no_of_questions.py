# Generated by Django 4.2.13 on 2024-07-05 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='no_of_questions',
            field=models.BigIntegerField(default=10),
        ),
    ]