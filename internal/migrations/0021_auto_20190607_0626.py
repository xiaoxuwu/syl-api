# Generated by Django 2.2.2 on 2019-06-07 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0020_merge_20190607_0626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='url',
            field=models.CharField(max_length=200),
        ),
    ]
