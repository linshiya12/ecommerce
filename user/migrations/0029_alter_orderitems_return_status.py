# Generated by Django 5.1.2 on 2024-12-14 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0028_orderitems_cancel_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='return_status',
            field=models.CharField(choices=[('Returned', 'Returned'), ('Not Returned', 'Not Returned')], default='Not Returned', max_length=20),
        ),
    ]
