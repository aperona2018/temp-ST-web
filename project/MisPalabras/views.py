import datetime
import json
import random
import urllib.request
from time import timezone
from xml.sax import ContentHandler
from xml.sax import make_parser

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from .models import Palabra, Comentario, Voto



# Create your views here.

def conseguirValoresPalabras():
    lista_palabras = Palabra.objects.all()
    num_palabras = len(lista_palabras)

    if (num_palabras > 0):
        palabraRandom = random.choice(lista_palabras)
    else:
        palabraRandom = "No hay palabras."

    return lista_palabras, num_palabras, palabraRandom


def crearListaMasVotadas():
    lista_palabras, num_palabras, palabraRandom = conseguirValoresPalabras()
    lista_votadas = sorted(lista_palabras, key=lambda p: p.votos)[::-1]
    lista_mas_votadas = []
    num_pals = 0
    for palabra in lista_votadas:
        if (num_pals < 10):
            lista_mas_votadas.append(palabra)
            num_pals += 1
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
    lista_palabras, num_palabras, palabraRandom = conseguirValoresPalabras()


    lista_palabras_index = lista_palabras[::-1]
    lista_index = []
    lista_aux = []
    i = 1
    for palabra in lista_palabras_index:
        lista_aux.append(palabra)
        if ((i % 5) == 0):
            lista_index.append(lista_aux)
            lista_aux = []
        i += 1

    if len(lista_aux) != 0:
        lista_index.append(lista_aux)


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
                    url = '/MisPalabras/error'
                    redirect(url)

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
               'lista_votadas': lista_mas_votadas, 'lista_index': lista_index }
    return HttpResponse(template.render(context, request))



def get_palabra(request, pal):
    lista_mas_votadas = crearListaMasVotadas()
    lista_palabras, num_palabras, palabraRandom = conseguirValoresPalabras()
    lista_coms = []

    if (num_palabras > 0):
        palabraRandom = random.choice(lista_palabras)
    else:
        palabraRandom = "No hay palabras."


    if request.method == "POST":
        action = request.POST['action']

        if action == 'añadir palabra':
            text = parsearWiki(pal)[0]
            # Lo hacemos así para que no haya definiciones a medias
            textoSplit = text.split('.')
            definicion = ""
            for i in range(len(textoSplit) - 1):
                definicion += textoSplit[i]

            if len(definicion) == 0:
                definicion = "No hay definición en la wikipedia."

            palabra = Palabra(nombrePalabra=pal, definicion=definicion, autor=request.user, votos=0)
            palabra.save()

        elif action == 'Buscar palabra':
            body = request.body.decode('utf-8')
            partes_body = body.split('&')
            pal = partes_body[1].split('=')[1]

            url = '/MisPalabras/'
            url += pal
            return redirect(url)

        elif action == 'votar palabra':
            for palabra in lista_palabras:
                if pal == palabra.nombrePalabra:
                    print("traza palabra: " + pal)
                    voto = Voto(palabra=palabra, autor=request.user)
                    voto.save()
                    palabra.votos += 1
                    palabra.save()

        elif action == "Login":
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
                    url = '/MisPalabras/error'
                    redirect(url)

        elif action == 'Logout':
            logout(request)

        elif action == "comentar":
            print("Comentar")
            palabra = Palabra.objects.get(nombrePalabra=pal)
            comentario = request.POST['comentario']
            autor = request.user.get_username()
            fecha = datetime.datetime.now()
            com = Comentario(palabra=palabra, comentario=comentario, autor=autor, fecha=fecha)
            com.save()

    votos = 0
    for palabra in lista_palabras:  #-- TODO: Hacer una función con esto
        if pal == palabra.nombrePalabra:
            print("traza palabra: " + pal)
            votos = palabra.votos
            lista_coms = palabra.comentario_set.all()


    añadida = palabraAñadida(pal)
    try:
        text = parsearWiki(pal)[0]
        # Lo hacemos así para que no haya definiciones a medias
        textoSplit = text.split('.')
        definicion = ""
        for i in range(len(textoSplit) - 1):
            definicion += textoSplit[i]

        if len(definicion) == 0:
            definicion = "No hay definición en la wikipedia."
    except KeyError:
        definicion = "No hay definición en la wikipedia."

    image = parsearWiki(pal)[1]

    tiene_imagen = image != "No hay"

    template = loader.get_template('MisPalabras/palabra.html')

    palabra_votada = False
    for palabra in lista_palabras:
        if (palabra.nombrePalabra == pal):
            for voto in Voto.objects.all():
                if (voto.palabra == palabra) and (voto.autor == request.user.get_username()):
                    print("Ya votada")
                    palabra_votada = True


    print("Ya votada:", palabra_votada)

    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom, 'palabra': pal, 'definicion': definicion, 'imagen': image,
               'añadida': añadida, "votos": votos, 'lista_votadas': lista_mas_votadas , 'lista_comentarios': lista_coms,
               'imagen': image, 'tiene_imagen': tiene_imagen, 'palabra_votada': palabra_votada}

    return HttpResponse(template.render(context, request))


def get_ayuda(request):
    lista_mas_votadas = crearListaMasVotadas()
    lista_palabras, num_palabras, palabraRandom = conseguirValoresPalabras()

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
                    url = '/MisPalabras/error'
                    redirect(url)

        if action == 'Logout':
            logout(request)

    template = loader.get_template('MisPalabras/ayuda.html')
    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom, 'lista_votadas': lista_mas_votadas }

    return HttpResponse(template.render(context, request))


def get_usersPag(request):
    lista_mas_votadas = crearListaMasVotadas()
    lista_palabras, num_palabras, palabraRandom = conseguirValoresPalabras()

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
                    url = '/MisPalabras/error'
                    redirect(url)


        if action == 'Logout':
            logout(request)
            url = '/MisPalabras/'
            return redirect(url)

    palabras_añadidas = []
    for palabra in lista_palabras:
        print("autor: " + palabra.autor + " user: " + request.user.get_username())
        if palabra.autor == request.user.get_username():
            palabras_añadidas.append(palabra)

    palabras_añadidas = palabras_añadidas[::-1]

    comentarios_puestos = []

    for comentario in Comentario.objects.all():
        if comentario.autor == request.user.get_username():
            comentarios_puestos.append(comentario)

    comentarios_puestos = comentarios_puestos[::-1]


    template = loader.get_template('MisPalabras/miPagina.html')
    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom, 'lista_votadas': lista_mas_votadas, 'palabras_añadidas': palabras_añadidas,
               'comentarios_puestos': comentarios_puestos}

    return HttpResponse(template.render(context, request))


def get_error(request):
    lista_palabras, num_palabras, palabraRandom = conseguirValoresPalabras()
    template = loader.get_template('MisPalabras/error.html')
    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom}
    return HttpResponse(template.render(context, request))


def get_xml(request):
    pass

def get_json(request):
    json_str = "{"
    for palabra in Palabra.objects.all():
        json_str += f"\n \t '{palabra.nombrePalabra}'" + "{ \n"
        json_str += f"\t \t 'autor':{palabra.autor} \n"
        json_str += f"\t \t 'definicion': {palabra.definicion} \n"
        json_str += f"\t \t 'votos': {palabra.votos}" + "}\n"

    json_str += "}\n?format=json"

    file = open('MisPalabras.json', 'w')
    try:
        file.write(json_str)
    finally:
        file.close()

    lista_palabras, num_palabras, palabraRandom = conseguirValoresPalabras()
    lista_mas_votadas = crearListaMasVotadas()

    template = loader.get_template('MisPalabras/json.html')
    context = {'lista_palabras': lista_palabras, 'user': request.user.username, 'num_palabras': num_palabras,
               'palabraRandom': palabraRandom, 'lista_votadas': lista_mas_votadas}

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
    jsonStream = json.loads(response.read())
    xmlStream = urllib.request.urlopen(url_text)
    Parser = make_parser()
    Parser.setContentHandler(Handler())
    Parser.parse(xmlStream)
    texto = data[0]

    try:
        image = jsonStream['query']["pages"][data[1]]["thumbnail"]["source"]
    except KeyError:
        print("No hay imagen")
        image = "No hay"
    finally:
        print('imagen',image)

        return texto[0:500], image

