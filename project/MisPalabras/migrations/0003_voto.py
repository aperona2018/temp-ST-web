# Generated by Django 3.1.7 on 2022-06-23 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MisPalabras', '0002_comentario_fecha'),
    ]

    operations = [
        migrations.CreateModel(
            name='Voto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autor', models.CharField(max_length=16)),
                ('palabra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MisPalabras.palabra')),
            ],
        ),
    ]
