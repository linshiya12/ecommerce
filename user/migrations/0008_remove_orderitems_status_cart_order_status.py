# Generated by Django 5.1.2 on 2024-11-29 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_orderitems_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitems',
            name='status',
        ),
        migrations.AddField(
            model_name='cart_order',
            name='status',
            field=models.CharField(choices=[('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('pending', 'Pending')], default='processing', max_length=20),
        ),
    ]
