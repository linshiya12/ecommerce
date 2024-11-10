# Generated by Django 5.0.6 on 2024-11-10 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_remove_variant_colour_remove_variant_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variant',
            old_name='colour_code',
            new_name='colour',
        ),
        migrations.AlterField(
            model_name='category',
            name='category_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('disabled', 'Disabled'), ('rejected', 'Rejected'), ('in_review', 'In review')], default='in_review', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('disabled', 'Disabled'), ('rejected', 'Rejected'), ('in_review', 'In review')], default='in_review', max_length=50),
        ),
    ]