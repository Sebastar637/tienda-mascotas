import json
from .models import *

def cookieCart(request):
	try:
		cart = json.loads(request.COOKIES['cart'])
	except:
		cart = {}
		print('CART:', cart)

	items = []
	order = {'get_cart_total':0, 'get_cart_items':0}
	cartItems = order['get_cart_items']

	for i in cart:
		try:
			cartItems += cart[i]['cantidad']

			product = Product.objects.get(id=i)
			total = (product.precio * cart[i]['cantidad'])

			order['get_cart_total'] += total
			order['get_cart_items'] += cart[i]['cantidad']

			item = {
				'id':product.id,
				'producto':{
					'id':product.id,
					'nombre':product.nombre, 
					'precio':product.precio, 
				        'imageURL':product.imageURL
					}, 
				'cantidad':cart[i]['cantidad'],
				'get_total':total,
				}
			items.append(item)
		except:
			pass
			
	return {'cartItems':cartItems ,'order':order, 'items':items}

def cartData(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(cliente=customer, completado=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		cookieData = cookieCart(request)
		cartItems = cookieData['cartItems']
		order = cookieData['order']
		items = cookieData['items']

	return {'cartItems':cartItems ,'order':order, 'items':items}

def format_number(number):
    formatted_total = "{:,.0f}".format(number)
    return formatted_total.replace(",", ".")
