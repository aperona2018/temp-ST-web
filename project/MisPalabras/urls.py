from django.contrib import admin
from django.urls import path
from . import views
from project import settings

urlpatterns = [
    path('', views.index, name="Indice"),
    path('ayuda', views.get_ayuda, name="Ayuda"),
    path('MiPagina', views.get_usersPag, name="MiPagina"),
    path('<str:pal>', views.get_palabra, name="Palabra")
]