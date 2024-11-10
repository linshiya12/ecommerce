# Generated by Django 5.0.6 on 2024-11-10 08:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_category_category_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='size',
        ),
        migrations.AlterField(
            model_name='category',
            name='category_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('disabled', 'Disabled'), ('rejected', 'Rejected'), ('in_review', 'In review'), ('published', 'Published')], default='in_review', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('disabled', 'Disabled'), ('rejected', 'Rejected'), ('in_review', 'In review'), ('published', 'Published')], default='in_review', max_length=50),
        ),
        migrations.AlterField(
            model_name='variantimages',
            name='variant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.variant'),
        ),
        migrations.CreateModel(
            name='VariantSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('size', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.size')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.variant')),
            ],
        ),
    ]
