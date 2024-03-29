# Generated by Django 4.2.2 on 2023-07-03 22:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0003_typesofvp_velikiperegoni_name_of_the_race_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PilotsRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pilot', models.CharField(max_length=50, verbose_name='Pilot Name')),
                ('rating', models.FloatField(default=0, verbose_name='Pilot Rating')),
            ],
        ),
        migrations.AlterField(
            model_name='velikiperegoni',
            name='date_of_race',
            field=models.DateField(default=datetime.datetime(2023, 7, 4, 0, 30, 45, 237643), verbose_name='Date of race'),
        ),
    ]
