# Generated by Django 5.1.2 on 2024-12-09 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0009_alter_user_phoneno_delete_emailverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referral_code',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
