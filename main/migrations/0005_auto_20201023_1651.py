# Generated by Django 3.1.2 on 2020-10-23 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20201023_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='results',
            field=models.CharField(blank=True, max_length=8),
        ),
    ]