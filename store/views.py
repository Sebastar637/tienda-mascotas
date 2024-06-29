from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData
from .forms import ProductForm

def about_us(request):
    context = {}
    return render(request, 'store/about.html', context)

def index(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/index.html', context)

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

def login(request):
    context = {}
    return render(request, 'store/login.html', context)

def register(request):
    context = {}
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