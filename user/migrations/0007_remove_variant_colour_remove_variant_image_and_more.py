# Generated by Django 5.0.6 on 2024-11-10 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_variantsize_size_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='colour',
        ),
        migrations.RemoveField(
            model_name='variant',
            name='image',
        ),
        migrations.AddField(
            model_name='variant',
            name='colour_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='category_status',
            field=models.CharField(choices=[('rejected', 'Rejected'), ('published', 'Published'), ('in_review', 'In review'), ('disabled', 'Disabled'), ('draft', 'Draft')], default='in_review', max_length=50),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('rejected', 'Rejected'), ('published', 'Published'), ('in_review', 'In review'), ('disabled', 'Disabled'), ('draft', 'Draft')], default='in_review', max_length=50),
        ),
    ]