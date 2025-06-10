from django.test import TestCase, Client
from store.models import Customer, Product, Order, OrderItem
from django.contrib.auth.models import User
from django.urls import reverse
import json

# ----------------------------
# TESTS DEL MÓDULO: Registro de usuarios
# ----------------------------
# En esta clase se realizan pruebas sobre el proceso de registro de nuevos usuarios.
# Se contemplan registros exitosos, intentos con nombres o correos ya existentes, contraseñas
# no coincidentes y validaciones sobre campos obligatorios.
class RegisterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/register/'

    def test_reg_ok(self):
        response = self.client.post(self.url, {
            'username': 'usuario_test',
            'email': 'test@example.com',
            'password1': 'unaClaveSegura123',
            'password2': 'unaClaveSegura123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='usuario_test').exists())

    def test_reg_dup_user(self):
        User.objects.create_user(username='usuario_test', email='otro@correo.com', password='clave1234')
        response = self.client.post(self.url, {
            'username': 'usuario_test',
            'email': 'nuevo@email.com',
            'password1': 'otraClave123',
            'password2': 'otraClave123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El nombre de usuario ya está en uso')

    def test_reg_dup_email(self):
        User.objects.create_user(username='otro_usuario', email='test@example.com', password='clave1234')
        response = self.client.post(self.url, {
            'username': 'nuevo_usuario',
            'email': 'test@example.com',
            'password1': 'claveSegura123',
            'password2': 'claveSegura123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El correo electrónico ya está en uso')

    def test_reg_pwd_mismatch(self):
        response = self.client.post(self.url, {
            'username': 'usuario',
            'email': 'usuario@correo.com',
            'password1': 'clave123',
            'password2': 'diferente123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Las contraseñas no coinciden')

    def test_reg_pwd_empty(self):
        response = self.client.post(self.url, {
            'username': 'fallo_validacion',
            'email': 'fallo@correo.com',
            'password1': '',
            'password2': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='fallo_validacion').exists())


# ----------------------------
# TESTS DEL MÓDULO: Login de usuarios
# ----------------------------
# Se validan distintos escenarios al momento de iniciar sesión, incluyendo credenciales
# válidas, contraseñas erróneas, usuarios inexistentes, formularios vacíos y usuarios inactivos.
class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.customer = Customer.objects.create(usuario=self.user, nombre='Test User', email='test@example.com')

    def test_login_ok(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_login_bad_pwd(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nombre de usuario o contraseña incorrectos')

    def test_login_no_user(self):
        response = self.client.post(reverse('login'), {'username': 'nouser', 'password': 'somepass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nombre de usuario o contraseña incorrectos')

    def test_login_empty(self):
        response = self.client.post(reverse('login'), {'username': '', 'password': ''}) 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nombre de usuario o contraseña incorrectos')

    def test_login_inactive(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nombre de usuario o contraseña incorrectos')


# ----------------------------
# TESTS DEL MÓDULO: Exploración de productos
# ----------------------------
# Verifica el correcto renderizado de productos en la página de inicio, incluyendo casos como
# ausencia de productos, imágenes faltantes, precios formateados y visibilidad del carrusel.
class ProductExplorationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product1 = Product.objects.create(
            nombre='Pelota para gato',
            precio=2500,
            imagen='products/pelota.jpg',
        )
        self.product2 = Product.objects.create(
            nombre='Rascador de cartón',
            precio=4500,
            imagen=None,
        )

    def test_index_shows_products(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pelota para gato')
        self.assertContains(response, 'Rascador de cartón')

    def test_index_default_img(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'img/default.png')

    def test_index_no_products(self):
        Product.objects.all().delete()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Agregar al Carrito')

    def test_index_carousel_cond(self):
        Product.objects.exclude(id=self.product1.id).delete()
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'd-none')

    def test_price_format(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, '$2.500')


# ----------------------------
# TESTS DEL MÓDULO: Carrito de compras
# ----------------------------
# Estas pruebas aseguran el correcto funcionamiento del carrito de compras. Incluyen agregar,
# quitar e incrementar productos, validar existencia y manejo sin autenticación.
class AddToCartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='clave123')
        self.customer = Customer.objects.create(usuario=self.user, nombre='test', email='test@email.com')
        self.product = Product.objects.create(nombre='Pelota', precio=5000, descripcion='Juguete para perro')
        self.url = '/update_item/'

    def test_cart_add_new(self):
        self.client.login(username='test', password='clave123')
        data = {'productId': self.product.id, 'action': 'add'}
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(OrderItem.objects.filter(pedido__cliente=self.customer, producto=self.product).exists())
        self.assertEqual(OrderItem.objects.get(pedido__cliente=self.customer, producto=self.product).cantidad, 1)

    def test_cart_add_existing(self):
        self.client.login(username='test', password='clave123')
        order = Order.objects.create(cliente=self.customer, completado=False)
        OrderItem.objects.create(pedido=order, producto=self.product, cantidad=1)
        data = {'productId': self.product.id, 'action': 'add'}
        self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        order_item = OrderItem.objects.get(pedido=order, producto=self.product)
        self.assertEqual(order_item.cantidad, 2)

    def test_cart_remove_last(self):
        self.client.login(username='test', password='clave123')
        order = Order.objects.create(cliente=self.customer, completado=False)
        OrderItem.objects.create(pedido=order, producto=self.product, cantidad=1)
        data = {'productId': self.product.id, 'action': 'remove'}
        self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertFalse(OrderItem.objects.filter(pedido=order, producto=self.product).exists())

    def test_cart_invalid_product(self):
        self.client.login(username='test', password='clave123')
        data = {'productId': 9999, 'action': 'add'}
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_cart_unauth(self):
        data = {'productId': self.product.id, 'action': 'add'}
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 401)


# ----------------------------
# TESTS DEL MÓDULO: Proceso de compra (checkout)
# ----------------------------
# Se testean diferentes rutas del proceso de compra: desde un checkout exitoso hasta errores
# por totales incorrectos, usuarios no autenticados o datos incompletos.
class CheckoutProcessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.customer = Customer.objects.create(usuario=self.user, nombre='testuser', email='test@example.com')
        self.product = Product.objects.create(nombre='Producto Test', precio=1000)
        self.client.login(username='testuser', password='testpass')

    def test_checkout_ok(self):
        cliente, _ = Customer.objects.get_or_create(
            usuario=self.user,
            defaults={'nombre': 'Test User', 'email': 'test@example.com'}
        )

        order = Order.objects.create(cliente=cliente)
        producto = Product.objects.create(nombre='Producto Test', precio=10000)
        OrderItem.objects.create(producto=producto, pedido=order, cantidad=2)

        total_correcto = str(order.get_cart_total)
        data = {
            'form': {'total': total_correcto},
            'shipping': {}
        }

        response = self.client.post('/process_order/', json.dumps(data), content_type='application/json')
        order.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(order.completado)

    def test_checkout_wrong_total(self):
        cliente = Customer.objects.create(usuario=None, nombre='Test User', email='test@example.com')
        order = Order.objects.create(cliente=cliente)

        producto = Product.objects.create(nombre='Producto Test', precio=10000)
        OrderItem.objects.create(producto=producto, pedido=order, cantidad=1)

        data = {
            'form': {'total': '999.999'},
            'shipping': {}
        }

        response = self.client.post('/process_order/', json.dumps(data), content_type='application/json')
        order.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(order.completado)

    def test_checkout_unauth(self):
        self.client.logout()
        response = self.client.post('/process_order/', json.dumps({'form': {'total': '2000'}}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_missing_total(self):
        Order.objects.filter(cliente=self.customer, completado=False).delete()

        Order.objects.create(cliente=self.customer, completado=False)
        OrderItem.objects.create(pedido=Order.objects.first(), producto=self.product, cantidad=1)

        with self.assertRaises(KeyError):
            self.client.post('/process_order/', json.dumps({'form': {}}), content_type='application/json')
