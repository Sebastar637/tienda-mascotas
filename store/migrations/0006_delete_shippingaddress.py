# Generated by Django 4.1.2 on 2024-06-29 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_order_completado_order_id_transaccion'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ShippingAddress',
        ),
    ]
