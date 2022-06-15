import json
import random
import urllib.request
from xml.sax import ContentHandler
from xml.sax import make_parser

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from .models import Palabra


# Create your views here.

lista_palabras = Palabra.objects.all()
num_palabras = len(lista_palabras)

if (num_palabras > 0):
    palabraRandom = random.choice(lista_palabras)
else:
    palabraRandom = "No hay palabras."


def crearListaMasVotadas():
    lista_votadas = sorted(lista_palabras, key=lambda p: p.votos)[::-1]
    lista_mas_votadas = []
    lista_test = []
    num_pals = 0
    for palabra in lista_votadas:
        if (num_pals <= 10) or (num_pals <= len(lista_votadas)):
            lista_mas_votadas.append(palabra)
            lista_test.append(palabra.nombrePalabra)
            num_pals += 1
    print(lista_test)
    return lista_mas_votadas


def palabraAñadida(pal):
    lista_palabras = Palabra.objects.all()

    for palabra in lista_palabras:
        if pal == palabra.nombrePalabra:
            return True
    return False


@csrf_exempt
def index(request):
    lista_mas_votadas = crearListaMasVotadas()

    if (num_palabras > 0):
        palabraRandom = random.choice(lista_palabras)
    else:
        palabraRandom = "No hay palabras."

    if request.method == "POST":
        action = request.POST['action']

        if action == "Login":
            username = request.POST['usuario']
            password = request.POST['contraseña']
            user = authenticate(request, username=username, password=password)
            if (user in User.objects.all()):
                login(request, user)
            else:
                try:
                    user = User.objects.create_user(username, 'myemail@mail.com', password)
                    user.save()
                    login(request, user)
                except IntegrityError:
                    print("TRAZA - Error al crear usuario")  # -- TODO: Mensaje de error

        if action == 'Logout':
            logout(request)

        if action == 'Buscar palabra':
            body = request.body.decode('utf-8')
            partes_body = body.split('&')
            pal = partes_body[1].split('=')[1]

            url = '/MisPalabras/'
            url += pal
            return redirect(url)


    template = loader.get_template('MisPalabras/index.html')
    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras, 'palabraRandom': palabraRandom,
               'lista_votadas': lista_mas_votadas }
    return HttpResponse(template.render(context, request))



def get_palabra(request, pal):
    lista_mas_votadas = crearListaMasVotadas()

    if (num_palabras > 0):
        palabraRandom = random.choice(lista_palabras)
    else:
        palabraRandom = "No hay palabras."


    if request.method == "POST":
        action = request.POST['action']

        if action == 'añadir':
            body = request.body.decode('utf-8')
            print("BODY:" + body)
            partes_body = body.split('&')
            pal = partes_body[1].split('=')[1]
            definicion = partes_body[2].split('=')[1]
            autor = request.user
            votos = 0
            print(pal)
            print(definicion)
            print(autor)

            palabra = Palabra(nombrePalabra=pal, definicion=definicion, autor=autor, votos=votos)
            palabra.save()

        if action == 'Buscar palabra':
            body = request.body.decode('utf-8')
            partes_body = body.split('&')
            pal = partes_body[1].split('=')[1]

            url = '/MisPalabras/'
            url += pal
            return redirect(url)

        if action == 'votar':
            body = request.body.decode('utf-8')
            partes_body = body.split('&')
            pal = partes_body[1].split('=')[1]
            for palabra in lista_palabras:
                if pal == palabra.nombrePalabra:
                    print("traza palabra: " + pal)
                    palabra.votos += 1
                    palabra.save()

        if action == "Login":
            username = request.POST['usuario']
            password = request.POST['contraseña']
            user = authenticate(request, username=username, password=password)
            if (user in User.objects.all()):
                login(request, user)
            else:
                try:
                    user = User.objects.create_user(username, 'myemail@mail.com', password)
                    user.save()
                    login(request, user)
                except IntegrityError:
                    print("TRAZA - Error al crear usuario")  # -- TODO: Mensaje de error

        if action == 'Logout':
            logout(request)

    for palabra in lista_palabras:  #-- TODO: Hacer una función con esto
        if pal == palabra.nombrePalabra:
            print("traza palabra: " + pal)
            votos = palabra.votos


    añadida = palabraAñadida(pal)

    text = parsearWiki(pal)[0]
    # Lo hacemos así para que no haya definiciones a medias
    textoSplit = text.split('.')
    definicion = ""
    for i in range(len(textoSplit) - 1):
        definicion += textoSplit[i]
    image = parsearWiki(pal)[1]  # -- TODO Meter imagen

    template = loader.get_template('MisPalabras/palabra.html')

    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom, 'palabra': pal, 'definicion': definicion, 'imagen': image,
               'añadida': añadida, "votos": votos, 'lista_votadas': lista_mas_votadas }

    return HttpResponse(template.render(context, request))


def get_ayuda(request):
    lista_mas_votadas = crearListaMasVotadas()

    if request.method == "POST":
        action = request.POST['action']

        if action == 'Buscar palabra':
            body = request.body.decode('utf-8')
            partes_body = body.split('&')
            pal = partes_body[1].split('=')[1]

            url = '/MisPalabras/'
            url += pal
            return redirect(url)

        if action == "Login":
            username = request.POST['usuario']
            password = request.POST['contraseña']
            user = authenticate(request, username=username, password=password)
            if (user in User.objects.all()):
                login(request, user)
            else:
                try:
                    user = User.objects.create_user(username, 'myemail@mail.com', password)
                    user.save()
                    login(request, user)
                except IntegrityError:
                    print("TRAZA - Error al crear usuario")  # -- TODO: Mensaje de error

        if action == 'Logout':
            logout(request)

    template = loader.get_template('MisPalabras/ayuda.html')
    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom, 'lista_votadas': lista_mas_votadas }

    return HttpResponse(template.render(context, request))


def get_usersPag(request):
    lista_mas_votadas = crearListaMasVotadas()

    if request.method == "POST":
        action = request.POST['action']

        if action == 'Buscar palabra':
            body = request.body.decode('utf-8')
            partes_body = body.split('&')
            pal = partes_body[1].split('=')[1]

            url = '/MisPalabras/'
            url += pal
            return redirect(url)

        if action == "Login":
            username = request.POST['usuario']
            password = request.POST['contraseña']
            user = authenticate(request, username=username, password=password)
            if (user in User.objects.all()):
                login(request, user)
            else:
                try:
                    user = User.objects.create_user(username, 'myemail@mail.com', password)
                    user.save()
                    login(request, user)
                except IntegrityError:
                    print("TRAZA - Error al crear usuario")  # -- TODO: Mensaje de error

        if action == 'Logout':
            logout(request)
            url = '/MisPalabras/'
            return redirect(url)

    palabras_añadidas = []
    for palabra in lista_palabras:
        print("autor: " + palabra.autor + " user: " + request.user.get_username())
        if palabra.autor == request.user.get_username():
            palabras_añadidas.append(palabra)


    template = loader.get_template('MisPalabras/miPagina.html')
    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom, 'lista_votadas': lista_mas_votadas, 'palabras_añadidas': palabras_añadidas}

    return HttpResponse(template.render(context, request))


data = ['', '', '']

class Handler(ContentHandler):
    def __init__(self):
        self.inContent = False
        self.content = ""

    def startElement(self, name, attrs):
        if name == 'extract':
            self.inContent = True
        if name == 'page':
            data[1] = attrs.get('pageid')
            data[2] = attrs.get('title')

    def endElement(self, name):
        if name == 'extract':
            self.inContent = False
            data[0] = self.content
            self.content = ""

    def characters(self, chars):
        if self.inContent:
            self.content = self.content + chars


#----------- Parseo de datos en wiki
def parsearWiki(palabra):
    url_text = "https://es.wikipedia.org/w/api.php?action=query&format=xml&titles=" + palabra + "&prop=extracts&exintro&explaintext"
    url_img = "https://es.wikipedia.org/w/api.php?action=query&titles=" + palabra + "&prop=pageimages&format=json&pithumbsize=300" # ????

    response = urllib.request.urlopen(url_img)
    xmlStream = urllib.request.urlopen(url_text)
    jsonStream = json.loads(response.read())
    Parser = make_parser()
    Parser.setContentHandler(Handler())
    Parser.parse(xmlStream)
    texto = data[0]

    # TODO Source de la imagen?

    return texto[0:500], jsonStream['query']["pages"][data[1]]
