# Generated by Django 5.0.6 on 2024-10-30 13:20

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0008_emailverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phoneno',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None),
        ),
        migrations.DeleteModel(
            name='EmailVerification',
        ),
    ]
