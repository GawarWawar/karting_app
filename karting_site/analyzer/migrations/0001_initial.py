# Generated by Django 4.2.2 on 2023-07-03 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VelikiPeregoni',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pilot', models.CharField(max_length=100, verbose_name='Pilot')),
                ('avarage_lap_time', models.FloatField(verbose_name='Avarage Lap Time')),
            ],
        ),
    ]