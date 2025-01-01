from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauth.models import User
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from django.utils import timezone

STOCK_STATUS = (
        ('Stock_In','stock_in'),
        ('Stock_Out','stock_out'),
    )
    
STATUS_CHOICE=(
    ("processing","Processing"),
    ("shipped","Shipped"),
    ("delivered","Delivered"),
    ("cancelled","Cancelled"),
    ("out for Delivery","Out for Delivery"),
    ("Returned","Returned"),
)

STATUS=(
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("rejected","Rejected"),
    ("in_review","In review"),
    ("published","Published"),
)

RATING=(
    (1,"★☆☆☆☆"),
    (2,"★★☆☆☆"),
    (3,"★★★☆☆"),
    (4,"★★★★☆"),
    (5,"★★★★★"),
)
VARIANTS=(
    ('None','None'),
    ('Size','Size'),
    ('Colour','Colour'),
    ('Size-Colour','Size-Colour')
)

FEATURED_CHOICE = (
    ("featured","featured"),
    ("not_featured","not_featured"),
)

PAYMENT_METHOD_CHOICES = (
    ('COD', 'Cash on Delivery'),
    ("razorpay", "Razorpay"),
    ('wallet', 'wallet'),
    
)

RETURN_STATUS_CHOICES = (
    ('Returned', 'Returned'),
    ('Not Returned', 'Not Returned'),
    )

CANCEL_STATUS_CHOICES = (
    ('Cancelled', 'Cancelled'),
    ('Not Cancelled', 'Not Cancelled'),
    )

REFUND_STATUS_CHOICES = (
        ("processing","processing"),
        ('Not Refunded', 'Not Refunded'),
        ('Refunded', 'Refunded'),
    )

def user_directory_path(instance,filename):
    user_id = instance.user.id if hasattr(instance, 'user') else 'default'
    return 'user_{0}/{1}'.format(user_id, filename)
    

class Category(MPTTModel):
    cid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="cat",alphabet="abcdefgh12345")
    parent=TreeForeignKey('self',blank=True,null=True,related_name='children',on_delete=models.SET_NULL)
    title=models.CharField(max_length=100,default="Shirt")
    category_status=models.CharField(choices=STATUS, max_length=50,default="in_review")

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title
    
    def clean(self):
        # Prevent a category from being its own parent
        if self.parent == self:
            raise ValidationError('A category cannot be its own parent.')

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is checked before saving
        super().save(*args, **kwargs)


class Tags(models.Model):
    pass

class Brand(models.Model):
    bid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="bra",alphabet="abcdefgh12345")
    title=models.CharField(max_length=100,default="pollo")
    brand_status=models.CharField(choices=STATUS, max_length=50,default="in_review")

    def __str__(self):
        return self.title


class ProductOffer(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_offer')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Enter the discount percentage (e.g., 10.00 for 10%).")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        """Check if the offer is valid based on the date and active status."""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def apply_discount(self, price):
        """Apply the percentage discount to the given price if the offer is valid."""
        if self.is_valid():
            return price - (price * self.discount_percentage / 100)
        return price

    def __str__(self):
        return f"{self.discount_percentage}% off on {self.product.title}"


class BrandOffer(models.Model):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='Brand_offer')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Enter the discount percentage (e.g., 10.00 for 10%).")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        """Check if the offer is valid based on the date and active status."""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def apply_discount(self, price):
        """Apply the percentage discount to the given price if the offer is valid."""
        if self.is_valid():
            return price - (price * self.discount_percentage / 100)
        return price

    def __str__(self):
        return f"{self.discount_percentage}% off on {self.brand.title}"


class Product(models.Model): 
    
    pid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="pro",alphabet="abcdefgh12345")
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    brand=models.ForeignKey("Brand",on_delete=models.SET_NULL,null=True)
    title=models.CharField(max_length=100,default="Shirt")
    description=models.TextField(null=True,blank=True,default="This is the product.")
    price=models.DecimalField(max_digits=15, decimal_places=2,default="199")
    specification =models.TextField(null=True,blank=True)
    discounted_price=models.DecimalField(max_digits=15, decimal_places=2,default="0")
    # tags=models.ForeignKey(Tags,on_delete=models.SET_NULL,null=True)
    product_status=models.CharField(choices=STATUS, max_length=50,default="in_review")
    featured=models.CharField(choices=FEATURED_CHOICE, max_length=50, default="not_featured")
   
    sku=ShortUUIDField(unique=True,length=10,max_length=30,prefix="sku",alphabet="abcdefgh12345")
    date=models.DateField(null=True,blank=True)

    class Meta:
        verbose_name_plural="Products"
    
    def is_stock_out(self):
        """ Check if all variants of the product are out of stock """
        return not self.indproduct.filter(variant_status="published", variant__stock="stock_in").exists()

    def __str__(self):
        return self.title

class Review(models.Model):
    product=models.ForeignKey("Product", on_delete=models.CASCADE,related_name="review")  
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")  
    review = models.TextField()
    rating = models.IntegerField(choices=RATING,default=None)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "product reviews"
    
    def __str__(self):
        return self.product.title
    
    def get_rating(self):
        return self.rating
    

    
class Variant(models.Model):
   
    vid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="var",alphabet="abcdefgh12345")
    product=models.ForeignKey(Product,related_name='indproduct',on_delete=models.SET_NULL,null=True)
    colour=models.CharField(max_length=50, null=True,blank=True)
    variant_status=models.CharField(choices=STATUS, max_length=50,default="in_review")

    def is_stock_out(self):
        """ Check if all sizes of the variant are out of stock """
        return not self.variant.filter(stock="stock_in").exists()
    def __str__(self):
        return f"{self.colour}"    



class VariantSize(models.Model):
    size_choices = (
        ('xxl','xxl'),
        ('xl','xl'),
        ('lg','lg'),
        ('md','md'),
        ('sm','sm'),
        ('xs' ,'xs')
    )
    variant=models.ForeignKey("Variant",related_name="variant",on_delete=models.CASCADE)
    size=models.CharField(max_length=10, choices=size_choices)
    size_status=models.CharField(choices=STATUS, max_length=50,default="in_review")
    quantity=models.PositiveIntegerField(default=0)
    stock=models.CharField(choices=STOCK_STATUS,max_length=50,default="stock_in")

    def __str__(self):
        return self.size
    
    def save(self, *args, **kwargs):
       if self.quantity==0:
            self.stock="stock_out"
       else:
            self.stock="stock_in"
    
       super().save(*args, **kwargs)


class VariantImages(models.Model):
    image=models.ImageField(upload_to="variant_image",default="colour.jpg")
    variant=models.ForeignKey(Variant,on_delete=models.SET_NULL,null=True)

    class Meta:
        verbose_name_plural="Variant images"



    



########################################## cart, order, Orderitems and address #######################################
########################################## cart, order, Orderitems and address #######################################
########################################## cart, order, Orderitems and address #######################################


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='cart_user')
    session_key = models.CharField(max_length=255, null=True, blank=True)  # For unauthenticated users
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total(self):
        total = sum(item.total_price() for item in self.items.all())
        return total
    def __str__(self):
        return f"Cart ({self.user})" if self.user else f"Cart (Session: {self.session_key})"


class CartItem(models.Model):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color_variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True, related_name='color_items')
    size_variant = models.ForeignKey(VariantSize, on_delete=models.SET_NULL, null=True, blank=True, related_name='size_items')
    image = models.ForeignKey(VariantImages, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"  


# address
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state= models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=False, null=False) 
    email=models.EmailField(max_length=255)

    def __str__(self):
        return f"{self.first_name}-{self.last_name}-{self.street}-{self.city}-{self.state}-{self.country}-{self.postal_code}-{self.phone}"

class Cart_Order(models.Model):
    user = models.IntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    paid_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, default="COD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='processing')
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state= models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=False, null=False) 
    email=models.EmailField(max_length=255)

    def __str__(self):
        return f"Order {self.user} - {self.status}"


class OrderItems(models.Model):
    order = models.ForeignKey("Cart_Order", on_delete=models.CASCADE, related_name="order_item")
    invoice_no = ShortUUIDField(unique=True, length=10, max_length=50, prefix="Orderid", alphabet="abcdefgh12345")
    product = models.CharField(max_length=200)
    image = models.ImageField(upload_to='order_images/', null=True, blank=True)
    colour = models.CharField(max_length=200)
    size = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    return_status = models.CharField(choices=RETURN_STATUS_CHOICES,max_length=20, default='Not Returned')  # Not Returned, Returned
    refund_status = models.CharField(choices=REFUND_STATUS_CHOICES,max_length=20, default='Not Refunded')  # Not Refunded, Refunded
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Refund Amount
    cancel_status = models.CharField(choices=CANCEL_STATUS_CHOICES,max_length=20, default='Not Cancelled')  # Not Returned, Returned
    refund_processed = models.BooleanField(default=False)

    def return_item(self):
        if self.return_status == 'Not Returned':
            self.return_status = 'Returned'
            self.refund_amount = self.price
            self.refund_status = 'processing'
            self.save()
            return True
        return False
    
    def cancel_item(self):
        if self.cancel_status == 'Not Cancelled':
            self.cancel_status = 'Cancelled'
            self.refund_amount = self.price
            self.refund_status = 'processing'
            self.save()
            return True
        return False

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe(f'<img src="/media/{self.image}" width="50" height="50" />')

    def __str__(self):
        return f"OrderItem {self.invoice_no} - {self.product}"

class Wallet(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def add_to_wallet(self, amount):
        self.balance += amount
        self.save()

    def __str__(self):
        return f"{self.user}'s Wallet"

class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount_percentage= models.DecimalField(max_digits=5, decimal_places=2, help_text="Enter the discount percentage (e.g., 10.00 for 10%).")
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    start_date=models.DateField(null=True)
    end_date=models.DateField(null=True)
    usage_limit=models.IntegerField(default=1)
    used_count=models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now().date()  # Ensure it's a date comparison
        return (
            self.active and
            self.start_date <= now <= self.end_date and
            self.used_count < self.usage_limit 
        )

    def apply_discount(self, total_price):
        return total_price - (total_price * self.discount_percentage / 100)

    def increment_usage(self):
        self.used_count += 1
        self.save()

    def __str__(self):
        return self.code

class CouponUsage(models.Model):
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages', null=True, blank=True)
    used_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('coupon', 'user')  
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.user} used {self.coupon} on {self.used_at}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='wishlist_user')
    session_key = models.CharField(max_length=255, null=True, blank=True)  # For unauthenticated users
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist ({self.user})" if self.user else f"Cart (Session: {self.session_key})"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey("Wishlist", on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color_variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True, related_name='wish_color_items')
    size_variant = models.ForeignKey(VariantSize, on_delete=models.SET_NULL, null=True, blank=True, related_name='wish_size_items')
    image = models.ForeignKey(VariantImages, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"  