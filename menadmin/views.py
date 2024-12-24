from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from user.models import *
from userauth.models import *
from django.contrib import messages
from datetime import datetime
from django.urls import reverse
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from io import BytesIO
from django.http import JsonResponse
from django.db.models import Sum, F,Prefetch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import re
from collections import defaultdict
import json
from decimal import Decimal


# Create your views here.
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def productlist(request):
    products=Product.objects.all()
    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context={
        "products":products,
        "message": message,
        "message_type": message_type,
    }
    
    return render(request,"adminproductlist.html",context)


@user_passes_test(lambda u: u.is_superuser,login_url='error')
def productview(request,id):
    products=get_object_or_404(Product,id=id)
    variant_colour = Variant.objects.filter(product__id=id)
    first_color = variant_colour.first()
    variant_size = VariantSize.objects.filter(variant=first_color)
    variant_image= VariantImages.objects.filter(variant=first_color)
    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context={
        "products":products,
        "variant_colour":variant_colour,
        "variant_size":variant_size,
        "variant_image":variant_image,
        "message": message,
        "message_type": message_type,
    }
    return render(request,"adproductview.html",context)


# edit product
@never_cache
def productedit(request,id):
    if request.method=="POST":
        category_id = request.POST.get("category")
        brand_id = request.POST.get("brand")
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        specification = request.POST.get("specification")
        product_status = request.POST.get("product_status")
        featured = request.POST.get("featured")
        date = request.POST.get("date")
        updated = request.POST.get("updated")

        #Check required fields
        required_fields = [category_id, brand_id, title, description, price,specification,featured, product_status, date, updated]
        if any(field == "" for field in required_fields):
            request.session['message']="All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/adproductedit/{id}")

        #Retrieve ForeignKey instances
        try:
            category = Category.objects.get(id=category_id)
            brand = Brand.objects.get(id=brand_id)
        except (Category.DoesNotExist, Brand.DoesNotExist) as e:
            request.session['message']=f"Invalid selection for {str(e).split()[0]}."
            request.session['message_type']="warning"
            return redirect(f"/adproductedit/{id}")

        #update product
        try:
            product=Product.objects.get(id=id)
            product.category = category
            product.brand = brand
            product.title = title
            product.description = description
            product.price =float(price)
            product.specification = specification
            product.product_status = product_status
            product.featured = featured
            product.date = date
            product.updated = updated
            product.save()

            request.session['message']="Product updated successfully."
            request.session['message_type']="success"
            return redirect(f"/adproductview/{id}") 
        except Exception as e:
            request.session['message']=f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/adproductedit/{id}")
    product = Product.objects.get(id=id)
    category = Category.objects.all()
    brand = Brand.objects.all()
    user = User.objects.all()


    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "category": category,
        "brand": brand,
        "user": user,
        "product":product,
        "message": message,
        "message_type": message_type,
    }

    return render(request,"adproductedit.html",context)


# addproduct
@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def productadd(request):
    category = Category.objects.all()
    brand = Brand.objects.all()
    user = User.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        brand_id = request.POST.get("brand")
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        specification = request.POST.get("specification")
        product_status = request.POST.get("product_status")
        featured = request.POST.get("featured") # Converts to boolean
        date = request.POST.get("date")
        updated = request.POST.get("updated")

        #Check required fields
        required_fields = [category_id, brand_id, title, description, price,featured, specification, product_status, date, updated]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect("/adproductadd")

        #Retrieve ForeignKey instances
        try:
            category = Category.objects.get(id=category_id)
            brand = Brand.objects.get(id=brand_id)
        except (Category.DoesNotExist, Brand.DoesNotExist) as e:
            request.session['message']= f"Invalid selection for {str(e).split()[0]}."
            request.session['message_type']="warning"
            return redirect("/adproductadd")

        #Save the product

        try:
            product=Product.objects.create(category=category,brand=brand,title=title,description=description,price=float(price),specification=specification,product_status=product_status,featured=featured,date=date,updated=updated)
            request.session['message']= "Product added successfully."
            request.session['message_type']="success"
            return redirect("/adminproductlist")

        except Exception as e:
            request.session['message']=f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect("/adproductadd")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "message":message,
        "message_type":message_type,
        "category": category,
        "brand": brand,
        "user": user
    }
    return render(request, "adproductadd.html", context)



# addvariantsize
@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def addvariantsize(request,id):
    variant = Variant.objects.get(id=id)
    
    if request.method == "POST":
        variant = request.POST.get("variant")
        size = request.POST.get("size")
        quantity = request.POST.get("quantity")
        stock = request.POST.get("stock")

        #Check required fields
        required_fields = [variant,size,quantity,stock]
        if any(field == "" for field in required_fields):
            request.session['message']="All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/addvariantsize/{id}")


        if VariantSize.objects.filter(size=size,variant__id=id).exists():
            request.session['message']= "this size already exists."
            request.session['message_type']="warning"
            return redirect(f"/addvariantsize/{id}")

        if int(quantity)<0:
            request.session['message']= "Quantity cannot be negative."
            request.session['message_type']="warning"
            return redirect(f"/addvariantsize/{id}")

        #Retrieve ForeignKey instances
        try:
            variant = Variant.objects.get(id=id)
        except (Variant.DoesNotExist,) as e:
            request.session['message']=f"Invalid selection for {str(e).split()[0]}."
            request.session['message_type']="warning"
            return redirect(f"/addvariantsize/{id}")


        #Save the variant size
        try:
            variantsize=VariantSize.objects.create(variant=variant,size=size,quantity=int(quantity),stock=stock)
            request.session['message']= "Product added successfully."
            request.session['message_type']="success"
            return redirect(f"/adshowvariant/{id}")

        except Exception as e:
            request.session['message']=f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/addvariantsize/{id}")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "variant": variant,
        "message":message,
        "message_type":message_type
    }
    return render(request, "addvariantsize.html", context)


# editvariantsize
@never_cache
def variantsizedit(request, id):
    try:
        variantsize = VariantSize.objects.get(id=id)
    except VariantSize.DoesNotExist:
        request.session['message']= "The requested Variant Size does not exist."
        request.session['message_type']="warning"
        return redirect(f"/adshowvariant/{variantsize.variant.id}")

    if request.method == "POST":
        variant_id = request.POST.get("variant")
        size = request.POST.get("size")
        size_status = request.POST.get("size_status")
        stock = request.POST.get("stock")
        quantity = request.POST.get("quantity")

        #Check required fields
        required_fields = [variant_id, size, size_status, stock, quantity]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/variantsizedit/{id}")

        if VariantSize.objects.filter(size=size,variant__id=id,size_status=size_status,stock=stock,quantity=quantity).exists():
            request.session['message']="this size already exists."
            request.session['message_type']="warning"
            return redirect(f"/variantsizedit/{id}")

        if int(quantity)<0:
            request.session['message']="Quantity cannot be negative."
            request.session['message_type']="warning"
            return redirect(f"/variantsizedit/{id}")

        try:
            variant = Variant.objects.get(id=variant_id)
        except Variant.DoesNotExist:
            request.session['message']= "The selected Variant does not exist."
            request.session['message_type']="warning"
            return redirect(f"/variantsizedit/{id}")

        #Update Variant Size
        try:
            variantsize.variant = variant
            variantsize.size = size
            variantsize.quantity = int(quantity)
            variantsize.stock = stock
            variantsize.size_status = size_status
            variantsize.save()

            request.session['message']="Size updated successfully."
            request.session['message_type']="success"
            return redirect(f"/adshowvariant/{variantsize.variant.id}") 

        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/variantsizedit/{id}")

    
    variants = Variant.objects.filter(id=variantsize.variant.id)

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context = {
        "variantsize": variantsize,
        "variants": variants,
        "message":message,
        "message_type":message_type
    }
    return render(request, "advariantsizedit.html", context)


def Variantcolouredit(request,id):
    colour=Variant.objects.get(id=id)
    if request.method == "POST":
        newcolour = request.POST.get("colour")
        variant_status = request.POST.get("variant_status")

        required_fields = [newcolour,variant_status]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/variantcolouredit/{id}")

        if Variant.objects.filter(colour=newcolour).exclude(id=id).exists():
            request.session['message']="this colour already exists."
            request.session['message_type']="warning"
            return redirect(f"/variantcolouredit/{id}")

        try:
            colour.colour = newcolour
            colour.variant_status = variant_status
            colour.save()

            request.session['message']="colour updated successfully."
            request.session['message_type']="success"
            return redirect(f"/adshowvariant/{id}") 

        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/variantcolouredit/{id}")
    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "colour": colour,
        "message":message,
        "message_type":message_type
    }
    return render(request,"editvariantcolour.html",context)

# variantview
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def variantview(request,id):
    variant = Variant.objects.get(id=id)
    variant_images=VariantImages.objects.filter(variant__id=id)
    variant_size=VariantSize.objects.filter(variant__id=id)

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "variant":variant,
        "variant_images":variant_images,
        "variant_size":variant_size,
        "message":message,
        "message_type":message_type
    }
    return render(request,"adshowvariant.html",context)

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def addvariant(request, id):
    product = Product.objects.get(id=id)
    
    if request.method == "POST":
        colour = request.POST.get("colour")
        variant_status = request.POST.get("variant_status")

        #Check required fields
        required_fields = [colour,variant_status]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/addvariant/{id}")

        #Retrieve ForeignKey instances
        try:
            product = Product.objects.get(id=id)
        except (Product.DoesNotExist,) as e:
            request.session['message']= f"Invalid selection for {str(e).split()[0]}."
            request.session['message_type']="warning"
            return redirect(f"/addvariant/{id}")

        if Variant.objects.filter(colour=colour,product__id=id).exists():
            request.session['message']= "A variant with this colour already exists."
            request.session['message_type']="warning"
            return redirect(f"/addvariant/{id}")

        #Save product

        try:
            variant=Variant.objects.create(product=product,colour=colour,variant_status=variant_status)
            request.session['message']="Product added successfully."
            request.session['message_type']="success"
            for i in range(1, 5):
                image_data = request.POST.get(f"image_data{i}")
                if image_data:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image = ContentFile(base64.b64decode(imgstr), name=f"variant_{i}.{ext}")
                    VariantImages.objects.create(variant=variant, image=image)

            return redirect((f"/adproductview/{id}"))

        except Exception as e:
            request.session['message']=f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/addvariant/{id}")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "message":message,
        "message_type":message_type
    }
    return render(request, "addvariant.html",context)


@never_cache
def imageedit(request, id, var_id):
    variantimage = VariantImages.objects.get(id=id)
    if request.method == "POST":
        image_data = request.POST.get("image_data")

        try:
            variant = Variant.objects.get(id=var_id)
        except Variant.DoesNotExist as e:
            request.session['message']= f"Invalid selection for {str(e).split()[0]}."
            request.session['message_type']="warning"
            return redirect(f"/adeditimage/{id}")

        # If image data is provided
        if image_data:
            try:
                #base64
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f"variant_image.{ext}")
                
                #Save
                variantimage.image = image_data
                variantimage.variant = variant
                variantimage.save()

                request.session['message']= "Image updated successfully."
                request.session['message_type']="success"
                return redirect(f"/adshowvariant/{var_id}")

            except Exception as e:
                request.session['message']= f"An unexpected error occurred: {str(e)}"
                request.session['message_type']="warning"
                return redirect(f"/adeditimage/{id}")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context = {
        "variantimage": variantimage,
        "message":message,
        "message_type":message_type
    }
    return render(request, "adeditimage.html", context)

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def categoryview(request):
    category=Category.objects.all()
    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "category":category,
        "message":message,
        "message_type":message_type
    }
    return render(request,"adcategorylist.html",context)

@never_cache
def categoryedit(request, id):
    try:
        category = Category.objects.get(id=id) 
    except:
        request.session['message']= "Category does not exist."
        request.session['message_type']="error"
        return redirect("/categoryview")

    allcategories = Category.objects.all()  
    if request.method == "POST":
        parent_id = request.POST.get("parent")  
        title = request.POST.get("category")  
        category_status = request.POST.get("category_status")  

        #required fields
        required_fields = [title, category_status]
        if any(field.strip() == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/categoryedit/{id}")

        try:
            if parent_id and parent_id != "None":
                try:
                    parent_category = Category.objects.get(id=parent_id)
                    category.parent = parent_category
                except Category.DoesNotExist:
                    request.session['message']= "Invalid parent category selected."
                    request.session['message_type']="warning"
                    return redirect(f"/categoryedit/{id}")
            else:
                category.parent = None

            #update
            category.title = title
            category.category_status = category_status
            category.save()

            request.session['message']= "Category updated successfully."
            request.session['message_type']="success"
            return redirect("/categoryview")

        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/categoryedit/{id}")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context = {
        "category": category,
        "allcategories": allcategories,
        "message":message,
        "message_type":message_type
    }
    return render(request, "adeditcategory.html", context)

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def categoryadd(request):
    if request.method == "POST":
        title = request.POST.get("title")
        parent_id = request.POST.get("parent")  
        category_status = request.POST.get("category_status")

        if not title or not category_status:
            request.session['message']= "Title and status are required."
            request.session['message_type']="warning"
            return redirect(reverse("categoryadd"))

        try:
            parent = None
            if parent_id:
                try:
                    parent = Category.objects.get(id=parent_id)
                except Category.DoesNotExist:
                    request.session['message']= "Selected parent category does not exist."
                    request.session['message_type']="warning"
                    return redirect(reverse("categoryadd"))

            # Save the category
            category = Category.objects.create(
                title=title,
                parent=parent,
                category_status=category_status
            )

            request.session['message']= "Category added successfully."
            request.session['message_type']="success"
            return redirect(reverse("categoryview"))

        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(reverse("categoryadd"))

    all_categories = Category.objects.all()  
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context = {
        "all_categories": all_categories,
        "message":message,
        "message_type":message_type
        }
    return render(request, "adcategoryadd.html", context)


@user_passes_test(lambda u: u.is_superuser,login_url='error')
def brand_list(request):
    brand=Brand.objects.all()
    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context={
        "brand":brand,
        "message":message,
        "message_type":message_type
    }
    return render(request,"adbrandlist.html",context)

@never_cache
def brandedit(request,id):
    brand=Brand.objects.get(id=id)
    if request.method=="POST":
        title=request.POST.get("brand")
        brand_status=request.POST.get("brand_status")
        
        required_fields = [title,brand_status]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/brandedit/{id}")

        if Brand.objects.filter(title=title,brand_status=brand_status).exists():
            request.session['message']= "this brand already exists."
            request.session['message_type']="warning"
            return redirect(f"/brandedit/{id}")

        try:
            brand.title=title
            brand.brand_status=brand_status
            brand.save()
            return redirect("/brandview")
        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/brandedit/{id}")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "brand":brand,
        "message":message,
        "message_type":message_type
    }

    return render(request,"adeditbrand.html",context)

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def brandadd(request):
    all_brand=Brand.objects.all()
    if request.method=="POST":
        brand=request.POST.get("brand")
        brand_status=request.POST.get("brand_status")

        required_fields = [brand,brand_status]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect("/brandadd")

        if Brand.objects.filter(title=brand,brand_status=brand_status).exists():
            request.session['message']= "this brand already exists."
            request.session['message_type']="warning"
            return redirect("/brandadd")

        try:
            brand=Brand.objects.create(title=brand,brand_status=brand_status)
            request.session['message']= "brand is successfully added"
            request.session['message_type']="success"
            return redirect("/brandview")
        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect("/brandadd")
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "message":message,
        "message_type":message_type
    }
    return render(request,"addbrand.html",context)

# User login
@never_cache
def admin_login(request):
    # if request.user.is_authenticated:
    #     return redirect("/home")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            request.session['message']= "Login successful!"
            request.session['message_type']="success"
            return redirect("/admindashboard")
        else:
            request.session['message']= "Invalid email or password"
            request.session['message_type']="warning"
            return redirect("/login")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context={
        "message":message,
        "message_type":message_type
    }
    return render(request, "adlogin.html",context)

# logout function
def adminlogout(request):
    logout(request)
    return redirect("/login")

def error_view(request):
    request.session['message']= "only superusers are authorised for this function"
    request.session['message_type']="error"
    return redirect('/login')



#################################################### user managment ################################################

# user details
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def User_details(request):
    users=User.objects.all().order_by("-id")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "users":users,
        "message": message,
        "message_type": message_type,
    }    
    return render(request,"ad-userlist.html",context)

#################################################### order managment ################################################

# orderlisting
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def Order_list(request):
    orders=Cart_Order.objects.all().order_by("-id")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "orders":orders,
        "message": message,
        "message_type": message_type,
    }    
    return render(request,"ad_orderlist.html",context)

# orderitem view
def Order_View(request,id):
    order=Cart_Order.objects.get(id=id)
    orderitems=OrderItems.objects.filter(order__id=id)
   
    for item in orderitems:
        total=item.order.total_price
    context = {
        "order": order,
        "orderitems": orderitems,
        "total":total,
    }
    return render(request,"ad_orderview.html",context)

def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        try:
            order = Cart_Order.objects.get(id=order_id)
            order.status = new_status
            order.save()

            return JsonResponse({'message': 'Order status updated successfully!'})

        except Cart_Order.DoesNotExist:
            return JsonResponse({'message': 'Order not found!'}, status=404)

    return JsonResponse({'message': 'Invalid request method!'}, status=400)

def update_refund_status(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_status = request.POST.get('status')
       
        try:
            order = OrderItems.objects.get(id=item_id)
            order.refund_status = new_status
            order.save()

            return JsonResponse({'message': 'refund status updated successfully!'})

        except OrderItems.DoesNotExist:
            return JsonResponse({'message': 'Ordered item not found!'}, status=404)

    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@user_passes_test(lambda u: u.is_superuser,login_url='error')
def All_Offers(request):
    product_offer=ProductOffer.objects.all()
    brand_offer=BrandOffer.objects.all()

    
    context={
        'product_offer':product_offer,
        'brand_offer':brand_offer,
        'message' : request.session.pop('message', None),
        'message_type' : request.session.pop('message_type', None)
    }
    return render(request,'ad_offer.html',context)

@never_cache
def edit_productoffer(request,id):
    offer=get_object_or_404(ProductOffer,id=id)
    products=Product.objects.filter(product_status="published")
    if request.method=="POST":
        product=request.POST.get("product")
        discount_percentage=request.POST.get("discount_percentage")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active")

        required_fields = [product,discount_percentage,start_date,end_date,is_active]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/editproductOffer/{id}")

        if ProductOffer.objects.filter(product=product,discount_percentage=discount_percentage,start_date=start_date,end_date=end_date,is_active=is_active).exclude(id=id).exists():
            request.session['message']= "this offer already exists."
            request.session['message_type']="warning"
            return redirect(f"editproductOffer/{id}")

        try:
            product = Product.objects.get(id=product)  # Ensure Product ID exists
            discount_percentage = float(discount_percentage)
            if discount_percentage < 0:
                raise ValueError("Invalid discount percentage.")

            start_date = start_date
            end_date = end_date
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")

            is_active = is_active == "True"

        except Product.DoesNotExist:
            request.session['message'] = "Invalid product selected."
            request.session['message_type'] = "warning"
            return redirect(f"/editproductOffer/{id}")
        except ValueError as e:
            request.session['message'] = str(e)
            request.session['message_type'] = "warning"
            return redirect(f"/editproductOffer/{id}")
        

        # edit
        try:
            offer.product=product
            offer.discount_percentage=discount_percentage
            offer.start_date=start_date
            offer.end_date=end_date
            offer.is_active="True"
            offer.save()

            request.session['message'] = "Offer updated successfully."
            request.session['message_type'] = "success"
            return redirect("All_Offers")
        
        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/editproductOffer/{id}")
    
    context={
        'offer':offer,
        'products':products,
        'message' : request.session.pop('message', None),
        'message_type' : request.session.pop('message_type', None)
    }

    return render(request,'ad_editproductOffer.html',context)

@never_cache
def AddProductoffer(request):
    products = Product.objects.filter(product_status="published")
    
    if request.method == "POST":
        product = request.POST.get("product")
        discount_percentage = request.POST.get("discount_percentage")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active")

        # Validate Required Fields
        required_fields = [product, discount_percentage, start_date, end_date, is_active]
        if any(field == "" for field in required_fields):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect("AddProductoffer")

        # Validate Product and Fields
        try:
            product = Product.objects.get(id=product)  # Ensure Product ID exists
            discount_percentage = float(discount_percentage)
            if discount_percentage < 0:
                raise ValueError("Invalid discount percentage.")

            start_date = start_date
            end_date = end_date
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")

            is_active = is_active == "True"

        except Product.DoesNotExist:
            request.session['message'] = "Invalid product selected."
            request.session['message_type'] = "warning"
            return redirect("AddProductoffer")
        except ValueError as e:
            request.session['message'] = str(e)
            request.session['message_type'] = "warning"
            return redirect("AddProductoffer")

        if ProductOffer.objects.filter(product=product, discount_percentage=discount_percentage, start_date=start_date, end_date=end_date,                          
        is_active=is_active).exists():
            request.session['message'] = "This offer already exists."
            request.session['message_type'] = "warning"
            return redirect("AddProductoffer")

        # Save the Offer
        try:
            ProductOffer.objects.create(
                product=product,
                discount_percentage=discount_percentage,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active
            )
            request.session['message'] = "Offer added successfully."
            request.session['message_type'] = "success"
            return redirect("All_Offers")
        
        except Exception as e:
            request.session['message'] = f"An unexpected error occurred: {str(e)}"
            request.session['message_type'] = "warning"
            return redirect("AddProductoffer")

    context = {
        'products': products,
        'message': request.session.pop('message', None),
        'message_type': request.session.pop('message_type', None)
    }

    return render(request, "ad_AddproductOffer.html", context)

@never_cache
def edit_brandoffer(request,id):
    offer=get_object_or_404(BrandOffer,id=id)
    Brands=Brand.objects.filter(brand_status="published")
    if request.method=="POST":
        brand=request.POST.get("brand")
        discount_percentage=request.POST.get("discount_percentage")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active")
       
        required_fields = [brand,discount_percentage,start_date,end_date,is_active]
        if any(field == "" for field in required_fields):
            request.session['message']= "All fields are required."
            request.session['message_type']="warning"
            return redirect(f"/editbrandOffer/{id}")

        if BrandOffer.objects.filter(brand=brand,discount_percentage=discount_percentage,start_date=start_date,end_date=end_date,is_active=is_active).exclude(id=id).exists():
            request.session['message']= "this offer already exists."
            request.session['message_type']="warning"
            return redirect(f"/editbrandOffer/{id}")

        try:
            brand = Brand.objects.get(id=brand)  # Ensure Product ID exists
            discount_percentage = float(discount_percentage)
            if discount_percentage < 0:
                raise ValueError("Invalid discount percentage.")

            start_date = start_date
            end_date = end_date
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")

            is_active = is_active == "True"

        except Brand.DoesNotExist:
            request.session['message'] = "Invalid brand selected."
            request.session['message_type'] = "warning"
            return redirect(f"/editbrandOffer/{id}")
        except ValueError as e:
            request.session['message'] = str(e)
            request.session['message_type'] = "warning"
            return redirect(f"/editbrandOffer/{id}")
        

        # edit
        try:
            offer.brand=brand
            offer.discount_percentage=discount_percentage
            offer.start_date=start_date
            offer.end_date=end_date
            offer.is_active=is_active
            offer.save()

            request.session['message'] = "Offer updated successfully."
            request.session['message_type'] = "success"
            return redirect("All_Offers")
        
        except Exception as e:
            request.session['message']= f"An unexpected error occurred: {str(e)}"
            request.session['message_type']="warning"
            return redirect(f"/editbrandOffer/{id}")
       
    context={
        'offer':offer,
        'Brands':Brands,
        'message' : request.session.pop('message', None),
        'message_type' : request.session.pop('message_type', None)
    }

    return render(request,'ad_editbrandOffer.html',context)

@never_cache
def AddBrandoffer(request):
    Brands = Brand.objects.filter(brand_status="published")
    
    if request.method == "POST":
        brand = request.POST.get("brand")
        discount_percentage = request.POST.get("discount_percentage")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active")

        # Validate Required Fields
        required_fields = [brand, discount_percentage, start_date, end_date, is_active]
        if any(field == "" for field in required_fields):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect("Addbrandoffer")

        # Validate Product and Fields
        try:
            brand = Brand.objects.get(id=brand)  # Ensure Product ID exists
            discount_percentage = float(discount_percentage)
            if discount_percentage < 0:
                raise ValueError("Invalid discount percentage.")

            start_date = start_date
            end_date = end_date
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")

            is_active = is_active == "True"

        except Product.DoesNotExist:
            request.session['message'] = "Invalid product selected."
            request.session['message_type'] = "warning"
            return redirect("AddBrandoffer")
        except ValueError as e:
            request.session['message'] = str(e)
            request.session['message_type'] = "warning"
            return redirect("AddBrandoffer")

        if BrandOffer.objects.filter(brand=brand, discount_percentage=discount_percentage, start_date=start_date, end_date=end_date,                          
        is_active=is_active).exists():
            request.session['message'] = "This offer already exists."
            request.session['message_type'] = "warning"
            return redirect("AddBrandoffer")

        # Save the Offer
        try:
            BrandOffer.objects.create(
                brand=brand,
                discount_percentage=discount_percentage,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active
            )
            request.session['message'] = "Offer added successfully."
            request.session['message_type'] = "success"
            return redirect("All_Offers")
        
        except Exception as e:
            request.session['message'] = f"An unexpected error occurred: {str(e)}"
            request.session['message_type'] = "warning"
            return redirect("AddBrandoffer")

    context = {
        'Brands': Brands,
        'message': request.session.pop('message', None),
        'message_type': request.session.pop('message_type', None)
    }

    return render(request, "ad_AddbrandOffer.html", context)


def delete_Brand_Offer(request,id):
    offer=BrandOffer.objects.get(id=id)
    offer.delete()
    request.session['message'] = "Offer deleted successfully"
    request.session['message_type'] = "success"
    return redirect("All_Offers")

def delete_Product_Offer(request,id):
    offer=ProductOffer.objects.get(id=id)
    offer.delete()
    request.session['message'] = "Offer deleted successfully"
    request.session['message_type'] = "success"
    return redirect("All_Offers")

def All_Coupons(request):
    coupon=Coupon.objects.all()

    context={
        'coupon':coupon,
        'message' : request.session.pop('message', None),
        'message_type' : request.session.pop('message_type', None)
    }

    return render(request,"Allcoupon.html",context)

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='error')
def AddCoupon(request):
    if request.method=="POST":
        code=request.POST.get("code")
        discount_percentage=request.POST.get("discount_percentage")
        start_date=request.POST.get("start_date")
        end_date=request.POST.get("end_date")
        usage_limit=request.POST.get("usage_limit")
        active=request.POST.get("active")
        min_purchase_amount=Decimal(request.POST.get("min_purchase_amount"))
        max_discount_amount=Decimal(request.POST.get("max_discount_amount"))

        # Validate Required Fields
        required_fields = [code, discount_percentage, start_date, end_date,active,usage_limit,max_discount_amount,min_purchase_amount]
        if any(field == "" for field in required_fields):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")

        if len(code) < 6 or len(code) > 8:
            request.session['message'] = "Coupon code must be between 6 and 8 characters long."
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")

        if not re.search(r'[a-zA-Z]', code) or not re.search(r'[0-9]', code):
            request.session['message'] = "Coupon code must contain at least one letter and one number."
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")
                
        if " " in code:
            request.session['message'] = "Coupon code cannot be empty or only spaces."
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")
        
        # Validate Product and Fields
        try:
            discount_percentage = float(discount_percentage)
            if discount_percentage < 0:
                raise ValueError("Invalid discount percentage.")
            
            if min_purchase_amount >= max_discount_amount:
                raise ValueError("Minimum purchase amount must be less than the maximum discount amount.")
            
            start_date = start_date
            end_date = end_date
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")

            usage_limit = int(usage_limit)
            if usage_limit < 0:
                raise ValueError("Usage limit cannot be less than 0.")
            active = active == "True"

        except ValueError as e:
            request.session['message'] = str(e)
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")

        if Coupon.objects.filter(code=code, discount_percentage=discount_percentage, start_date=start_date, end_date=end_date,                          
        active=active,usage_limit=usage_limit,min_purchase_amount=min_purchase_amount,max_discount_amount=max_discount_amount).exists():
            request.session['message'] = "This coupon already exists."
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")

        if Coupon.objects.filter(code=code).exists():
            request.session['message'] = "this coupon code is already exists."
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")
        try:
            coupon=Coupon.objects.create(code=code, discount_percentage=discount_percentage, start_date=start_date, end_date=end_date,active=active,usage_limit=usage_limit,max_discount_amount=max_discount_amount,min_purchase_amount=min_purchase_amount)
            request.session['message'] = "Coupon added successfully."
            request.session['message_type'] = "success"
            return redirect("All_Coupons")
        
        except Exception as e:
            request.session['message'] = f"An unexpected error occurred: {str(e)}"
            request.session['message_type'] = "warning"
            return redirect("AddCoupon")
        
    context={
        'message': request.session.pop('message', None),
        'message_type': request.session.pop('message_type', None)
    }

    return render(request,"Addcoupon.html",context)


@never_cache
def EditCoupon(request, id):
    coupon_code = Coupon.objects.get(id=id)
    if request.method == "POST":
        code = request.POST.get("code")
        discount_percentage = request.POST.get("discount_percentage")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        usage_limit = request.POST.get("usage_limit")
        active = request.POST.get("active")
        min_purchase_amount=Decimal(request.POST.get("min_purchase_amount"))
        max_discount_amount=Decimal(request.POST.get("max_discount_amount"))

        # Validate Required Fields
        required_fields = [code, discount_percentage, start_date, end_date, active,usage_limit,min_purchase_amount,max_discount_amount]
        if any(field == "" for field in required_fields):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")

        if len(code) < 6 or len(code) > 8:
            request.session['message'] = "Coupon code must be between 6 and 8 characters long."
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")

        if not re.search(r'[a-zA-Z]', code) or not re.search(r'[0-9]', code):
            request.session['message'] = "Coupon code must contain at least one letter and one number."
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")
                
        if " " in code:
            request.session['message'] = "Coupon code cannot be empty or only spaces."
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")
        
        # Validate Product and Fields
        try:
            discount_percentage = float(discount_percentage)
            if discount_percentage < 0:
                raise ValueError("Invalid discount percentage.")
            if min_purchase_amount >= max_discount_amount:
                raise ValueError("Minimum purchase amount must be less than the maximum discount amount.")
            
            start_date = start_date
            end_date = end_date
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")

            usage_limit = int(usage_limit)
            if usage_limit < 0:
                raise ValueError("Usage limit cannot be less than 0.")
            active = active == "True"

        except ValueError as e:
            request.session['message'] = str(e)
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")

        if Coupon.objects.filter(code=code, discount_percentage=discount_percentage, start_date=start_date, end_date=end_date,                          
        active=active,usage_limit=usage_limit,min_purchase_amount=min_purchase_amount,max_discount_amount=max_discount_amount).exists():
            request.session['message'] = "This coupon already exists."
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")
        
        # Check if coupon code already exists
        if Coupon.objects.filter(code=code).exclude(id=id).exists():
            request.session['message'] = "This coupon code already exists."
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")

        try:
            coupon_code.code = code
            coupon_code.discount_percentage = discount_percentage
            coupon_code.start_date = start_date
            coupon_code.end_date = end_date
            coupon_code.usage_limit = usage_limit
            coupon_code.active = active
            coupon_code.min_purchase_amount=min_purchase_amount
            coupon_code.max_discount_amount=max_discount_amount
            coupon_code.save()
            request.session['message'] = "Coupon updated successfully."
            request.session['message_type'] = "success"
            return redirect("All_Coupons")

        except Exception as e:
            request.session['message'] = f"An unexpected error occurred: {str(e)}"
            request.session['message_type'] = "warning"
            return redirect(f"/Editcoupon/{id}")

    context = {
        'coupon_code': coupon_code,
        'message': request.session.pop('message', None),
        'message_type': request.session.pop('message_type', None)
        }
    return render(request, "adeditCoupon.html", context)


def delete_Coupon(request,id):
    coupon=Coupon.objects.get(id=id)
    coupon.delete()
    request.session['message'] = "Coupon deleted successfully"
    request.session['message_type'] = "success"
    return redirect("All_Coupons")
        

@user_passes_test(lambda u: u.is_superuser,login_url='error')
def Sales_Report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    time_filter = request.GET.get('time_filter')  
    download_pdf = request.GET.get('download_pdf') 
    today = timezone.now().date()

    # orders query
    orders = Cart_Order.objects.all()

    # Apply time-based filter if selected
    if time_filter:
        if time_filter == 'daily':
            orders = orders.filter(created_at__date=today)
        elif time_filter == 'weekly':
            start_of_week = today - timedelta(days=today.weekday())  # Start of the current week
            orders = orders.filter(created_at__date__gte=start_of_week)
        elif time_filter == 'monthly':
            start_of_month = today.replace(day=1)  # First day of the current month
            orders = orders.filter(created_at__date__gte=start_of_month)
        elif time_filter == 'yearly':
            start_of_year = today.replace(month=1, day=1)  # First day of the current year
            orders = orders.filter(created_at__date__gte=start_of_year)

    # Apply date range filter if provided
    if start_date and end_date:
        orders = orders.filter(created_at__date__range=[start_date, end_date])

    # Calculate totals
    total_sales = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_discount = orders.aggregate(Sum('discount'))['discount__sum'] or 0
    total_order_count = orders.count()

    context = {
        'orders': orders,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'total_order_count': total_order_count,
        'start_date': start_date,
        'end_date': end_date,
        'time_filter': time_filter,
    }

    if download_pdf:
        response = generate_pdf_report(orders, total_sales, total_order_count,total_discount)
        return response
    return render(request, "adsalesreport.html", context)


def generate_pdf_report(orders, total_sales, total_order_count, total_discount):
    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Use ReportLab's SimpleDocTemplate for better pagination
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("<b>Sales Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Summary Section
    summary_text = f"""
    <b>Total Sales:</b> {total_sales:,.0f}<br/>
    <b>Total Orders:</b> {total_order_count}<br/>
    <b>Total Discounts:</b> {total_discount:,.0f}
    """
    summary = Paragraph(summary_text, styles['Normal'])
    elements.append(summary)
    elements.append(Spacer(1, 12))

    # Table Header
    table_data = [
        ["Order ID", "User", "Total Price", "Discount", "Payment Method", "Status", "Created At"]
    ]

    # Add orders to table data
    for order in orders:
        table_data.append([
            str(order.id),
            str(order.user),
            f"{order.total_price:,.0f}",
            f"{order.discount:,.0f}" if order.discount else "0",
            order.payment_method,
            order.get_status_display(),
            order.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    # Table Style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ])

    # Create Table
    table = Table(table_data, colWidths=[60, 100, 80, 80, 100, 70, 100])
    table.setStyle(table_style)

    # Calculate table height
    row_height = 18  # Approximate row height
    max_rows_per_page = int((11 * inch - 2 * inch) / row_height)  # Page height - margins
    current_data = table_data[:1]  # Start with headers

    for i, row in enumerate(table_data[1:], start=1):
        current_data.append(row)
        if len(current_data) > max_rows_per_page or i == len(table_data) - 1:
            elements.append(Table(current_data, colWidths=[60, 100, 80, 80, 100, 70, 100], style=table_style))
            elements.append(PageBreak())
            current_data = table_data[:1]  # Reset to headers for next page

    # Build the PDF
    doc.build(elements)

    return response


@user_passes_test(lambda u: u.is_superuser,login_url='error')
def dashboard(request):
    total_ordered = OrderItems.objects.count()
    total_cancelled = OrderItems.objects.filter(cancel_status='Cancelled').count()
    total_returned = OrderItems.objects.filter(return_status= 'Returned').count()

    best_selling_products = get_best_selling_products()
    best_selling_brand = get_top_selling_brands()
    best_selling_category = get_top_selling_category()

    today = timezone.now()

    # Filter orders by day, week, month, and year
    day_orders = Cart_Order.objects.filter(created_at__date=today.date())
    week_orders = Cart_Order.objects.filter(created_at__gte=today - timedelta(days=7))
    month_orders = Cart_Order.objects.filter(created_at__gte=today - timedelta(days=30))
    year_orders = Cart_Order.objects.filter(created_at__gte=today - timedelta(days=365))
    def get_chart_data(orders):
        return {
            'labels': [order.created_at.strftime('%Y-%m-%d') for order in orders],
            'data': [float(order.total_price) for order in orders]  
        }

    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context={
        'total_ordered':total_ordered,
        'total_cancelled':total_cancelled,
        'total_returned':total_returned,
        'best_selling_brand' : best_selling_brand,
        'best_selling_products': best_selling_products,
        'best_selling_category' : best_selling_category,
        'name': request.user.username,
        'day_data': json.dumps(get_chart_data(day_orders)), 
        'week_data': json.dumps(get_chart_data(week_orders)), 
        'month_data': json.dumps(get_chart_data(month_orders)),  
        'year_data': json.dumps(get_chart_data(year_orders)),
        "message":message,
        "message_type":message_type
    }
    return render(request,"admindashboard.html",context)


# top 10 best selling product
def get_best_selling_products():
    return OrderItems.objects.values('product').annotate(total_qty=Sum('qty')).order_by('-total_qty')[:10]

# top 10 best selling brand
def get_top_selling_brands():

    top_selling_products = OrderItems.objects.values('product').annotate(total_qty=Sum('qty')).order_by('-total_qty')[:10]
    brand_sales = defaultdict(int)
    
    for item in top_selling_products:
        product_name = item['product']
        try:
            product = Product.objects.get(title=product_name)
            brand_sales[product.brand.title] += item['total_qty']
        except Product.DoesNotExist:
            continue

    top_selling_brands = sorted(brand_sales.items(), key=lambda x: x[1], reverse=True)[:10]
    return top_selling_brands
    
# top 10 best selling category
def get_top_selling_category():

    top_selling_products = OrderItems.objects.values('product').annotate(total_qty=Sum('qty')).order_by('-total_qty')[:10]
    category_sales = defaultdict(int)
    
    for item in top_selling_products:
        product_name = item['product']
        try:
            product = Product.objects.get(title=product_name)
            category_sales[product.category.title] += item['total_qty']
        except Product.DoesNotExist:
            continue

    top_selling_category = sorted(category_sales.items(), key=lambda x: x[1], reverse=True)[:10]
    return top_selling_category
    
   