# Generated by Django 2.2.1 on 2019-05-13 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0010_auto_20190513_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='text',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]