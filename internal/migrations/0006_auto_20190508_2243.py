# Generated by Django 2.2.1 on 2019-05-08 22:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0005_auto_20190508_0331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
