from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name="index"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),

    path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

    path('product_list', views.product_list, name='product_list'),
    path('product_add/', views.product_add, name='product_add'),
    path('product_edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('product/delete/<int:pk>/', views.product_delete, name='product_delete'),
]