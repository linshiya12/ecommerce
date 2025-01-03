# Generated by Django 5.1.2 on 2024-11-29 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_remove_orderitems_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='status',
            field=models.CharField(choices=[('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('pending', 'Pending')], default='processing', max_length=20),
        ),
    ]
