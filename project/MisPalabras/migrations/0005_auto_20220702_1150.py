# Generated by Django 3.1.7 on 2022-07-02 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MisPalabras', '0004_palabra_linkimagen'),
    ]

    operations = [
        migrations.RenameField(
            model_name='palabra',
            old_name='linkImagen',
            new_name='imagen',
        ),
    ]