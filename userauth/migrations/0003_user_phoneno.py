# Generated by Django 5.0.6 on 2024-10-23 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0002_user_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phoneno',
            field=models.CharField(default=1, max_length=20, unique=True),
            preserve_default=False,
        ),
    ]
