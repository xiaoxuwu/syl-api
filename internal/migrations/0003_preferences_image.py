# Generated by Django 2.2.1 on 2019-05-03 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0002_auto_20190503_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferences',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
