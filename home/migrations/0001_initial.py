# Generated by Django 5.0.6 on 2024-11-10 06:14

import django.db.models.deletion
import home.models
import mptt.fields
import shortuuid.django_fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=10, max_length=30, prefix='bra', unique=True)),
                ('title', models.CharField(default='pollo', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CartOrderItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Colour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=10, max_length=30, prefix='siz', unique=True)),
                ('colour_code', models.CharField(max_length=50)),
                ('colour_title', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=10, max_length=30, prefix='siz', unique=True)),
                ('size', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=10, max_length=30, prefix='cat', unique=True)),
                ('title', models.CharField(default='Shirt', max_length=100)),
                ('category_status', models.CharField(choices=[('rejected', 'Rejected'), ('published', 'Published'), ('draft', 'Draft'), ('disabled', 'Disabled'), ('in_review', 'In review')], default='in_review', max_length=50)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='home.category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=10, max_length=30, prefix='pro', unique=True)),
                ('title', models.CharField(default='Shirt', max_length=100)),
                ('image', models.ImageField(default='product.jpg', upload_to=home.models.user_directory_path)),
                ('description', models.TextField(blank=True, default='This is the product.', null=True)),
                ('price', models.DecimalField(decimal_places=2, default='199', max_digits=15)),
                ('old_price', models.DecimalField(decimal_places=3, default='299', max_digits=15)),
                ('specification', models.TextField(blank=True, null=True)),
                ('product_status', models.CharField(choices=[('rejected', 'Rejected'), ('published', 'Published'), ('draft', 'Draft'), ('disabled', 'Disabled'), ('in_review', 'In review')], default='in_review', max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('in_stock', models.BooleanField(default=True)),
                ('featured', models.BooleanField(default=False)),
                ('digital', models.BooleanField(default=False)),
                ('sku', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=10, max_length=30, prefix='sku', unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.brand')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.category')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='Varient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=10, max_length=30, prefix='var', unique=True)),
                ('image', models.ImageField(default='colour.jpg', upload_to=home.models.user_directory_path)),
                ('price', models.DecimalField(decimal_places=2, default='199', max_digits=15)),
                ('old_price', models.DecimalField(decimal_places=3, default='299', max_digits=15)),
                ('colour', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.colour')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='indproduct', to='home.product')),
            ],
        ),
        migrations.CreateModel(
            name='VarientImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='colour.jpg', upload_to='varient_image')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('varient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.varient')),
            ],
            options={
                'verbose_name_plural': 'Varient images',
            },
        ),
        migrations.CreateModel(
            name='VarientSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('size', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.size')),
                ('varient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.varient')),
            ],
        ),
    ]
