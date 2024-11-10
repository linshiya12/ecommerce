from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauth.models import User
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError


STATUS_CHOICE={
    ("process","Processing"),
    ("shipped","Shipped"),
    ("delivered","Delivered")
}

STATUS={
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("rejected","Rejected"),
    ("in_review","In review"),
    ("published","Published"),
}

RATING={
    ("1","★☆☆☆☆"),
    ("2","★★☆☆☆"),
    ("3","★★★☆☆"),
    ("4","★★★★☆"),
    ("5","★★★★★"),
}

VARIANTS=(
    ('None','None'),
    ('Size','Size'),
    ('Colour','Colour'),
    ('Size-Colour','Size-Colour')
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

    def __str__(self):
        return self.title


# class Vendor(models.Model):
#     vid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="ven",alphabet="abcdefgh12345")
#     title=models.CharField(max_length=100,default="Nestify")
#     image=models.ImageField(upload_to=user_directory_path,default="vendor.jpg")
#     description=models.TextField(null=True,blank=True,default="iam an amazing vendor.")
   

#     address=models.CharField(max_length=100, default='123 Main Street')
#     contact=models.CharField(max_length=100, default='+912346767723')
#     chat_resp_time=models.CharField(max_length=100, default='100')
#     shipping_on_time=models.CharField(max_length=100, default='100')
#     authentic_rating=models.CharField(max_length=100, default='100')
#     days_return=models.CharField(max_length=100, default='100')
#     warrenty_period=models.CharField(max_length=100, default='100')

#     user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)

#     class Meta:
#         verbose_name_plural="Vendors"

#     def vendor_image(self):
#         return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

#     def _str_(self):
#         return self.title


class Colour(models.Model):
    cid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="siz",alphabet="abcdefgh12345")
    colour_code=models.CharField(max_length=50)
    colour_title=models.CharField(max_length=50)


    def __str__(self):
        return f"{self.colour_title}"

class Product(models.Model): 
    
    pid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="pro",alphabet="abcdefgh12345")
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    brand=models.ForeignKey("Brand",on_delete=models.SET_NULL,null=True)
    title=models.CharField(max_length=100,default="Shirt")
    description=models.TextField(null=True,blank=True,default="This is the product.")
    price=models.DecimalField(max_digits=15, decimal_places=2,default="199")
    old_price=models.DecimalField(max_digits=15, decimal_places=3,default="299")
    specification =models.TextField(null=True,blank=True)
   
    # tags=models.ForeignKey(Tags,on_delete=models.SET_NULL,null=True)
    product_status=models.CharField(choices=STATUS, max_length=50,default="in_review")
    status=models.BooleanField(default=True)
    in_stock=models.BooleanField(default=True)
    featured=models.BooleanField(default=False)
    digital=models.BooleanField(default=False)
   
    sku=ShortUUIDField(unique=True,length=10,max_length=30,prefix="sku",alphabet="abcdefgh12345")
    date=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(null=True,blank=True)

    class Meta:
        verbose_name_plural="Products"

    def __str__(self):
        return self.title

    def get_percentage(self):
        new_price=(self.old_price-self.price) / (self.old_price/100)
        return new_price
    


    
class VariantSize(models.Model):
    size_choices = (
        ('xxl' , 'xxl'),
        ('xl','xl'),
        ('lg','lg'),
        ('md','md'),
        ('sm','sm'),
        ('xs' ,'xs')
    )
    variant=models.ForeignKey("Variant",on_delete=models.CASCADE)
    size=models.CharField(max_length=10, choices=size_choices)
    quantity=models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.variant.product.title+' - '+self.size + " - " + self.variant.colour.colour_title
    

    

class Variant(models.Model):
    
   
    vid=ShortUUIDField(unique=True,length=10,max_length=30,prefix="var",alphabet="abcdefgh12345")
    product=models.ForeignKey(Product,related_name='indproduct',on_delete=models.SET_NULL,null=True)
    colour=models.CharField(max_length=50, null=True,blank=True)
    price=models.DecimalField(max_digits=15, decimal_places=2,default="199")
    old_price=models.DecimalField(max_digits=15, decimal_places=3,default="299")


    def __str__(self):
        return f"{self.product.title} {self.colour}"    
    
    


class VariantImages(models.Model):
    image=models.ImageField(upload_to="variant_image",default="colour.jpg")
    variant=models.ForeignKey(Variant,on_delete=models.SET_NULL,null=True)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="Variant images"



    



########################################## cart, order, Orderitems and address #######################################
########################################## cart, order, Orderitems and address #######################################
########################################## cart, order, Orderitems and address #######################################

class CartOrderItems(models.Model):
    "pass"


   





# Create your models here.