# Generated by Django 4.2.6 on 2023-10-24 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0012_fines'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fines',
            name='paid',
            field=models.IntegerField(default=0),
        ),
    ]