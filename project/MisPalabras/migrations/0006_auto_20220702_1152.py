# Generated by Django 3.1.7 on 2022-07-02 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MisPalabras', '0005_auto_20220702_1150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='palabra',
            name='imagen',
        ),
        migrations.AddField(
            model_name='palabra',
            name='linkImagen',
            field=models.TextField(default='STRING'),
        ),
    ]
