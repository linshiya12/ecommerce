# Generated by Django 5.0.6 on 2024-11-10 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('disabled', 'Disabled'), ('published', 'Published'), ('in_review', 'In review'), ('rejected', 'Rejected')], default='in_review', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('disabled', 'Disabled'), ('published', 'Published'), ('in_review', 'In review'), ('rejected', 'Rejected')], default='in_review', max_length=50),
        ),
    ]
