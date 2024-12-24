# Generated by Django 5.1.2 on 2024-12-17 02:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0032_alter_orderitems_colour_alter_orderitems_size'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='couponusage',
            unique_together={('coupon', 'user')},
        ),
        migrations.AddField(
            model_name='cart_order',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='coupon',
            name='max_discount_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='coupon',
            name='min_purchase_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.RemoveField(
            model_name='couponusage',
            name='discount_applied',
        ),
        migrations.RemoveField(
            model_name='couponusage',
            name='order',
        ),
    ]
