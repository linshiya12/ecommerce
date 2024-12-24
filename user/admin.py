from django.contrib import admin
from user.models import *

class VariantImagesAdmin(admin.TabularInline):
    model=VariantImages

class ProductAdmin(admin.ModelAdmin):
    # inlines = [ProductImagesAdmin]
    list_display = ['title','featured','product_status']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','parent_name']

    def save_model(self, request, obj, form, change):
        if obj.parent == obj:
            raise ValidationError('A category cannot be its own parent.')
        super().save_model(request, obj, form, change)
    def parent_name(self, obj):
        return obj.parent.title if obj.parent else None


# class VendorAdmin(admin.ModelAdmin):
#     list_display = ['title','vendor_image']

    


class VariantAdmin(admin.ModelAdmin):
    list_display = ['colour']
    inlines = [VariantImagesAdmin]


admin.site.register(ProductOffer),
admin.site.register(BrandOffer),
admin.site.register(Product,ProductAdmin)
admin.site.register(Category,CategoryAdmin)

admin.site.register(VariantSize)
admin.site.register(Variant,VariantAdmin)
admin.site.register(Brand),
admin.site.register(Cart),
admin.site.register(CartItem),
admin.site.register(ShippingAddress),
admin.site.register(Cart_Order),
admin.site.register(OrderItems),
admin.site.register(WishlistItem),
admin.site.register(Coupon),
admin.site.register(Wallet),
admin.site.register(Wishlist),
admin.site.register(Review),
admin.site.register(CouponUsage),






# Register your models here.
