from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from user.models import *
from django.http import JsonResponse


# Create your views here.
def create(request):
    products=Product.objects.filter(product_status="published", featured=True)
    products1=Product.objects.filter(product_status="published").order_by('-date')[:5]
    variant_colour = Variant.objects.all()
    
    # variant_colour = Variant.objects.filter(product__id=id)
    
    context={
        "products":products,
        "products1":products1,
        "variant_colour":variant_colour
    }
    # for product in products:
    #     if product.image is None or not product.image.name:  # Check if image exists
    #         print(f"No image for product: {product.title}")
    #     else:
    #         print("yes")
    return render(request,"home.html",context)

def contact(request):
    return render(request,"contact.html")

def blog(request):
    return render(request,"blog.html")

def cart(request):
    return render(request,"cart.html")

def wishlist(request):
    return render(request,"wishlist.html")

def shop(request):
    products=Product.objects.filter(product_status="published")
    
    context={
        "products":products
    }
    
    
    return render(request,"shop.html",context)

# individual product
def product(request,id):
    products=get_object_or_404(Product,id=id)
    variant_colour = Variant.objects.filter(product__id=id)
    first_color = variant_colour.first()
    variant_size = VariantSize.objects.filter(variant=first_color)
    variant_image= VariantImages.objects.filter(variant=first_color)
  
    context={
        "products":products,
        "variant_colour":variant_colour,
        "variant_size":variant_size,
        "variant_image":variant_image,
       
    }
    
    return render(request,"product.html",context)

from django.http import JsonResponse

def get_variant_images(request,id):
    
    variant_images =  VariantImages.objects.filter(variant__id = id)
    data = list(variant_images.values())
    print(data)
    return JsonResponse(data, safe=False)

    
