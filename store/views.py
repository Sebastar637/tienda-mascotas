from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.http import JsonResponse

import json
import datetime

from random import sample
from .models import * 
from .utils import cookieCart, cartData
from .forms import ProductForm

def about_us(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/about_us.html', context)

def index(request):
	products = Product.objects.all()
	random_products = sample(list(products), min(8, len(products)))

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'products':products, 'cartItems':cartItems, 'random_products': random_products}
	return render(request, 'store/index.html', context)

def product_detail(request, product_id):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    product = get_object_or_404(Product, id=product_id)
    products = Product.objects.all()

    context = {
        'product': product,
        'products':products, 
        'cartItems':cartItems
    }
    return render(request, 'store/product_detail.html', context)

def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(cliente=customer, completado=False)

	orderItem, created = OrderItem.objects.get_or_create(pedido=order, producto=product)

	if action == 'add':
		orderItem.cantidad = (orderItem.cantidad + 1)
	elif action == 'remove':
		orderItem.cantidad = (orderItem.cantidad - 1)

	orderItem.save()

	if orderItem.cantidad <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

    

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(cliente=customer, completado=False)
		total = data['form']['total']
		order.id_transaccion = transaction_id

		if total == order.get_cart_total:
			order.complete = True
		order.save()
	else:
		print('User is not logged in')

	return JsonResponse('Payment submitted..', safe=False)

def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('index')
		else:
			messages.error(request, 'Nombre de usuario o contraseña incorrectos')

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/login.html', context)


def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password1 = request.POST['password1']
		password2 = request.POST['password2']

		if password1 == password2:
			if User.objects.filter(username=username).exists():
				messages.error(request, 'El nombre de usuario ya está en uso')
			elif User.objects.filter(email=email).exists():
				messages.error(request, 'El correo electrónico ya está en uso')
			else:
				user = User.objects.create_user(username=username, email=email, password=password1)
				user.save()

				customer = Customer.objects.create(usuario=user, nombre=username, email=email)
				customer.save()

				login(request, user)
				messages.success(request, 'Registro exitoso')
				return redirect('index')
		else:
			messages.error(request, 'Las contraseñas no coinciden')
	
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/register.html', context)


def product_list(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request, 'store/product_list.html', context)

def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    context = {'form': form, 'form_title': 'Agregar Producto', 'button_text': 'Agregar'}
    return render(request, 'store/product_form.html', context)


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    context = {'form': form, 'form_title': 'Modificar Producto', 'button_text': 'Guardar Cambios'}
    return render(request, 'store/product_form.html', context)


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    
    context = {'product': product}
    return render(request, 'store/product_delete.html', context)