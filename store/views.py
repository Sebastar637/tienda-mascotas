from django.shortcuts import render
from .models import *

def index(request):
	products = Product.objects.all()
	context = {'products': products}
	return render(request, 'store/index.html', context)

def about(request):
    context = {}
    return render(request, 'store/about.html', context)

def cart(request):
	if request.user.is_authenticated:
		cliente = request.user.customer
		order, created = Order.objects.get_or_create(cliente=cliente, completado=False)
		items = order.orderitem_set.all()
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}

	context = {'items':items, 'order':order}
	return render(request, 'store/cart.html', context)

def checkout(request):
	if request.user.is_authenticated:
		cliente = request.user.customer
		order, created = Order.objects.get_or_create(cliente=cliente, completado=False)
		items = order.orderitem_set.all()
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}

	context = {'items':items, 'order':order}
	return render(request, 'store/checkout.html', context)

def login(request):
    context = {}
    return render(request, 'store/login.html', context)