from django.test import Client
from django.test import TestCase
import json
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from MisPalabras.models import Palabra, Comentario, Voto

# Create your tests here.

class Test(TestCase):

    def setUp(self):
        user = User.objects.create_user('testing', 'myemail@mail.com', 'testing')
        user.save()

        palabra = Palabra(nombrePalabra="silla", definicion="definicion de silla", autor="pepito", votos=0)
        palabra.save()


    def test_num_users(self):
        self.assertEquals(User.objects.all().count(), 1)

    #-- Pruebas de recursos con GET

    def test_get_index(self):
        c = Client()
        response = c.get('/MisPalabras/')
        self.assertEqual(response.status_code, 200)

    def test_get_palabra(self):
        c = Client()
        response = c.get('/MisPalabras/silla')
        self.assertEqual(response.status_code, 200)

    def test_get_ayuda(self):
        c = Client()
        response = c.get('/MisPalabras/ayuda')
        self.assertEqual(response.status_code, 200)

    def test_get_json(self):
        c = Client()
        response = c.get('/MisPalabras/json')
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        self.assertIn("?format=json", content)

    def test_get_xml(self):
        c = Client()
        response = c.get('/MisPalabras/xml')
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        self.assertIn("?format=xml", content)

    def test_get_miPagina(self):
        c = Client()
        response = c.get('/MisPalabras/MiPagina')
        self.assertEqual(response.status_code, 200)

    def test_get_error(self):
        c = Client()
        response = c.get('/MisPalabras/error')

        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn("ERROR: Algo salió mal :(", content)


    # -- Pruebas de recursos con POST


    def test_comentar(self):

        c = Client()

        response = c.post('/MisPalabras/silla', {'action': "comentar", 'comentario': "Comentario test"})

        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        self.assertIn('Comentario test', content)


    def test_añadir_palabra(self):

        c = Client()

        num_palabras_antes = len(Palabra.objects.all())

        response = c.post('/MisPalabras/pepe', {'action': "añadir palabra"})

        self.assertEqual(response.status_code, 200)

        response2 = c.get('/MisPalabras/pepe')
        num_palabras_despues = len(Palabra.objects.all())


        content = response2.content.decode('utf-8')

        self.assertIn('Palabra añadida', content)
        self.assertEqual(num_palabras_despues, num_palabras_antes + 1)


    def test_votar(self):
        c = Client()

        palabraTest = Palabra.objects.get(nombrePalabra="silla")

        votos_antes = palabraTest.votos

        response = c.post('/MisPalabras/silla', {'action': 'votar palabra'})
        self.assertEqual(response.status_code, 200)

        c.get('/MisPalabras/silla', {'action': 'votar palabra'})

        palabraTest1 = Palabra.objects.get(nombrePalabra="silla")
        votos_despues = palabraTest1.votos

        self.assertEqual(votos_despues, votos_antes + 1)

    def test_login(self):
        c = Client()
        response = c.post('/MisPalabras/', {'action': 'Login', 'usuario': "admin", 'contraseña': "admin"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Logeado como <h1>admin</h1>', content)

    def test_logout(self):
        c = Client()
        c.post('/MisPalabras/', {'action': 'Login', 'usuario': "admin", 'contraseña': "admin"})

        response = c.post('/MisPalabras/', {'action': 'Logout'})
        content = response.content.decode('utf-8')

        self.assertIn('<h2>Loguéate:</h2>', content)







