# Generated by Django 5.1.2 on 2024-12-13 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_product_discounted_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart_order',
            name='user',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
