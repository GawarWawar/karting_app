# Generated by Django 4.2.2 on 2023-06-26 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recorder', '0003_race_is_recorded'),
    ]

    operations = [
        migrations.RenameField(
            model_name='race',
            old_name='publish_time',
            new_name='publish_date',
        ),
    ]