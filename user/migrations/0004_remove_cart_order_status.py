# Generated by Django 5.1.2 on 2024-11-29 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_cart_order_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart_order',
            name='status',
        ),
    ]
