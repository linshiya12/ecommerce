# Generated by Django 5.1.2 on 2024-11-30 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_alter_cart_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='refund_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='refund_status',
            field=models.CharField(choices=[('processing', 'processing'), ('Not Refunded', 'Not Refunded'), ('Refunded', 'Refunded')], default='Not Refunded', max_length=20),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='return_status',
            field=models.CharField(choices=[('Returned', 'Returned'), ('Not Returned', 'Not Returned'), ('processing', 'processing')], default='Not Returned', max_length=20),
        ),
    ]
