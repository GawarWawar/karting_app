# Generated by Django 4.2.2 on 2024-04-12 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recorder', '0011_alter_race_date_record_finished_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='racerecords',
            name='team_number',
            field=models.CharField(max_length=10, verbose_name='team_number'),
        ),
    ]