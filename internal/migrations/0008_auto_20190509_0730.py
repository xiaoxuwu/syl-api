# Generated by Django 2.2.1 on 2019-05-09 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0007_auto_20190508_2347'),
    ]

    operations = [
        migrations.RenameField(
            model_name='preference',
            old_name='image',
            new_name='background_img',
        ),
        migrations.AddField(
            model_name='preference',
            name='profile_img',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
