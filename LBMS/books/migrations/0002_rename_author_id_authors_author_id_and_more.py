# Generated by Django 4.2.6 on 2023-10-20 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='authors',
            old_name='Author_Id',
            new_name='author_id',
        ),
        migrations.RenameField(
            model_name='authors',
            old_name='Name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='bookauthors',
            old_name='Author_Id',
            new_name='author_id',
        ),
        migrations.RenameField(
            model_name='bookauthors',
            old_name='Isbn',
            new_name='isbn',
        ),
        migrations.RenameField(
            model_name='books',
            old_name='Isbn',
            new_name='isbn',
        ),
        migrations.RenameField(
            model_name='books',
            old_name='Title',
            new_name='title',
        ),
        migrations.AlterUniqueTogether(
            name='bookauthors',
            unique_together={('author_id', 'isbn')},
        ),
    ]