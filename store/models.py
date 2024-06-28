from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
	usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	nombre = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.nombre


class Product(models.Model):
	nombre = models.CharField(max_length=200)
	precio = models.IntegerField()
	imagen = models.ImageField(null=True, blank=True)

	def __str__(self):
		return self.nombre

	@property
	def imageURL(self):
		try:
			url = self.imagen.url
		except:
			url = ''
		return url

class Order(models.Model):
	cliente = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	completado = models.BooleanField(default=False)
	id_transaccion = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.cantidad for item in orderitems])
		return total 

class OrderItem(models.Model):
	producto = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	pedido = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	cantidad = models.IntegerField(default=0, null=True, blank=True)

	@property
	def get_total(self):
		total = self.producto.precio * self.cantidad
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address