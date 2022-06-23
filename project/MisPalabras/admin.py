from django.contrib import admin
from .models import Palabra, Comentario, Voto

# Register your models here.
admin.site.register(Palabra)
admin.site.register(Comentario)
admin.site.register(Voto)

