# Generated by Django 5.1.2 on 2024-11-30 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_brandoffer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='old_price',
        ),
    ]
