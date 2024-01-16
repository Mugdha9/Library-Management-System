# Generated by Django 4.2.6 on 2023-10-22 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_alter_bookloans_date_in'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookAvailability',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=50)),
                ('borrowed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.borrowers')),
                ('isbn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.books')),
            ],
        ),
    ]
