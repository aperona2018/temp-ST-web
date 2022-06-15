from django.db import models

# Create your models here.


class Palabra(models.Model):
    nombrePalabra = models.TextField()
    definicion = models.TextField(max_length=50)
    votos = models.IntegerField()
    autor = models.CharField(max_length=16)


class Comentario(models.Model):
    comentario = models.TextField(max_length=50)
    palabra = models.ForeignKey('Palabra', on_delete=models.CASCADE)
    autor = models.CharField(max_length=16)
