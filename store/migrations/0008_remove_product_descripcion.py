# Generated by Django 4.1.2 on 2024-06-29 22:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_product_descripcion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='descripcion',
        ),
    ]