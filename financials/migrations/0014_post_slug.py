# Generated by Django 3.2.23 on 2023-12-09 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financials', '0013_auto_20231204_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(default='temp-slug', max_length=200, unique=True),
        ),
    ]