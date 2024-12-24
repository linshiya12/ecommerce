# Generated by Django 5.1.2 on 2024-12-02 13:09

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_wishlist_wishlistitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.CharField(blank=True, max_length=100, null=True)),
                ('used_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('discount_applied', models.DecimalField(decimal_places=2, help_text='The actual discount applied on this usage.', max_digits=10)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages', to='user.coupon')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupon_usages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-used_at'],
                'unique_together': {('coupon', 'user', 'order')},
            },
        ),
    ]
