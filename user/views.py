from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from user.models import *
from userauth.models import User
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q,Count,Avg,Sum
from userauth import views
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.http import HttpResponse
from datetime import datetime
from io import BytesIO
from django.core.files.storage import default_storage
from datetime import date



# Create your views here.
def create(request):
    products=Product.objects.filter(product_status="published", featured="featured")
    products1=Product.objects.filter(product_status="published").order_by('-date')[:5]
    variant_colour = Variant.objects.filter(variant_status="published")


    # featuredproduct
    featproduct_offer=[]
    for p in products:

        # stock
        product_is_stock_out = True
        variants_with_stock = []

        for var in p.indproduct.filter(variant_status="published"):
            if var.is_stock_out():
                stock_status = "Stock Out"
            else:
                stock_status = "In Stock"
                product_is_stock_out = False

            variants_with_stock.append({
                'variant': var,
                'stock_status': stock_status
            })


        # offer
        productoffer=ProductOffer.objects.filter(product=p,product__product_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')
        brandoffer=BrandOffer.objects.filter(brand=p.brand,brand__brand_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')
    
        offer=None
        discounted_price = p.price
        if productoffer and brandoffer:
            
            if productoffer[0].discount_percentage<brandoffer[0].discount_percentage:
                offer=brandoffer[0]
                discounted_price = offer.apply_discount(p.price)
            else:
                offer=productoffer[0]
                discounted_price = offer.apply_discount(p.price)
        elif productoffer:
            offer=productoffer[0]
            discounted_price = offer.apply_discount(p.price)
        elif brandoffer:
            offer=brandoffer[0]
            discounted_price = offer.apply_discount(p.price)

        featproduct_offer.append({
            'product':p,
            'offer':offer,
            'discounted_price':discounted_price,
            'product_is_stock_out': product_is_stock_out,
            'variants_with_stock': variants_with_stock
        })


    # trendy product
    trendy_offer=[]
    for p in products1:

        # stock
        product_is_stock_out = True
        variants_with_stock = []

        for var in p.indproduct.filter(variant_status="published"):
            if var.is_stock_out():
                stock_status = "Stock Out"
            else:
                stock_status = "In Stock"
                product_is_stock_out = False

            variants_with_stock.append({
                'variant': var,
                'stock_status': stock_status
            })

        # offer
        productoffer=ProductOffer.objects.filter(product=p,product__product_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')
        brandoffer=BrandOffer.objects.filter(brand=p.brand,brand__brand_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')

        discounted_price = p.price
        offer=None
        if productoffer and brandoffer:
           
            if productoffer[0].discount_percentage<brandoffer[0].discount_percentage:
                offer=brandoffer[0]
                discounted_price = offer.apply_discount(p.price)
            else:
                offer=productoffer[0]
                discounted_price = offer.apply_discount(p.price)
        elif productoffer:
            offer=productoffer[0]
            discounted_price = offer.apply_discount(p.price)
        elif brandoffer:
            offer=brandoffer[0]
            discounted_price = offer.apply_discount(p.price)
            

        trendy_offer.append({
            'product':p,
            'offer':offer,
            'discounted_price':discounted_price,
            'product_is_stock_out': product_is_stock_out,
            'variants_with_stock': variants_with_stock
        })
        

    # variant_colour = Variant.objects.filter(product__id=id)
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context={
        "featproduct_offer":featproduct_offer,
        "trendy_offer":trendy_offer,
        "variant_colour":variant_colour,
        "message": message,
        "message_type": message_type,
    
    }

    
    return render(request,"home.html",context)

def contact(request):
    return render(request,"contact.html")

def blog(request):
    return render(request,"blog.html")

def shop(request):
    products=Product.objects.filter(product_status="published")
    category=Category.objects.filter(category_status="published").exclude(parent=None)
    size=VariantSize.objects.filter(size_status="published").distinct("size")
    variant=Variant.objects.filter(variant_status="published").distinct("colour")
    brand=Brand.objects.filter(brand_status="published")

    sort_by = request.GET.get("sort_by", None)
    if sort_by:  
        products = sort_products(sort_by, products)

    product_offer=[]
    for p in products:
        
        # 
        reviews,avg_rating,double_avg_rating,rating_distribution = get_reviews_by_product(p.id)

        # stock
        product_is_stock_out = True
        variants_with_stock = []

        for var in p.indproduct.filter(variant_status="published"):
            if var.is_stock_out():
                stock_status = "Stock Out"
            else:
                stock_status = "In Stock"
                product_is_stock_out = False

            variants_with_stock.append({
                'variant': var,
                'stock_status': stock_status
            })


        # offer
        productoffer=ProductOffer.objects.filter(product=p,product__product_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')
        brandoffer=BrandOffer.objects.filter(brand=p.brand,brand__brand_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')
    
        offer=None
        discounted_price = p.price
        if productoffer and brandoffer:
            
            if productoffer[0].discount_percentage<brandoffer[0].discount_percentage:
                offer=brandoffer[0]
                discounted_price = offer.apply_discount(p.price)
            else:
                offer=productoffer[0]
                discounted_price = offer.apply_discount(p.price)
        elif productoffer:
            offer=productoffer[0]
            discounted_price = offer.apply_discount(p.price)
        elif brandoffer:
            offer=brandoffer[0]
            discounted_price = offer.apply_discount(p.price)
        p.discounted_price=discounted_price
        p.save()
        product_offer.append({
            'product':p,
            'offer':offer,
            'discounted_price':discounted_price,
            'product_is_stock_out': product_is_stock_out,
            'variants_with_stock': variants_with_stock,
            'double_avg_rating':double_avg_rating,
            'reviews' : reviews
        })

    context={
        "product_offer":product_offer,
        "category":category,
        "size":size,
        "variant":variant,
        "brand":brand,
        'sort_by':sort_by
    }
    
    
    return render(request,"shop.html",context)

from django.db.models import Case, When, Value, F,DecimalField
def sort_products(sort_by, products):
    if sort_by == "popularity":
        popular_products = OrderItems.objects.values('product').annotate(
            total_orders=Count('order', distinct=True),
            total_quantity=Sum('qty'),
            total_revenue=Sum('total')
        ).order_by('-total_orders')
        product_titles = [item['product'] for item in popular_products]

        # Filter the original products
        products = products.filter(title__in=product_titles)

        # Sort the products
        products = sorted(products, key=lambda p: product_titles.index(p.title))

    elif sort_by == "price_low_high":
        products = products.order_by('discounted_price')
    elif sort_by == "price_high_low":
        products = products.order_by('-discounted_price')
    elif sort_by == "average_ratings":
        products = products.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
    elif sort_by == "new_arrivals":
        products = products.order_by('-date')
    elif sort_by == "a_to_z":
        products = products.order_by('title')
    elif sort_by == "z_to_a":
        products = products.order_by('-title')
    else:
        products = products.order_by('-id')

    return products


# individual product
def product(request,id):
    products=get_object_or_404(Product,id=id)
    related_product=Product.objects.filter(product_status="published",category=products.category,category__category_status="published").exclude(id=id)
    variant_colour = Variant.objects.filter(product__id=id,variant_status="published")
    first_color = variant_colour.first() if variant_colour.exists() else None
    variant_size = VariantSize.objects.filter(variant=first_color,size_status="published")
    variant_image= VariantImages.objects.filter(variant=first_color)
    # review
    reviews,avg_rating,double_avg_rating,rating_distribution = get_reviews_by_product(id)
    make_review = True
    if request.user.is_authenticated:
        user_review_count=Review.objects.filter(user=request.user,product__id=id).count()
        if user_review_count > 0:
            make_review = False

    # stock
    product_is_stock_out = products.is_stock_out() 
    variant_is_stock_out = first_color.is_stock_out() if first_color else False
    size_is_stock_out = all(size.stock == "stock_out" for size in variant_size) if variant_size else False

    productoffer=ProductOffer.objects.filter(product=products,product__product_status="published",start_date__lte=timezone.now(),is_active=True,end_date__gte=timezone.now()).order_by('-discount_percentage')
    brandoffer=BrandOffer.objects.filter(brand=products.brand,brand__brand_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')

    # offer
    offer1=None
    discounted_price1=products.price
   
    if productoffer and brandoffer:
        if productoffer[0].discount_percentage<brandoffer[0].discount_percentage:
            offer1=brandoffer[0]
            discounted_price1 = offer1.apply_discount(products.price)
        else:   
            offer1=productoffer[0]
            discounted_price1 = offer1.apply_discount(products.price)
    elif productoffer:
        offer1=productoffer[0]
        discounted_price1 = offer1.apply_discount(products.price)
    elif brandoffer:
        offer1=brandoffer[0]
        discounted_price1 = offer1.apply_discount(products.price)
    

    product_offer=[]
    for p in related_product:

        # stock
        product_is_stock_out = True
        variants_with_stock = []

        for var in p.indproduct.filter(variant_status="published"):
            if var.is_stock_out():
                stock_status = "Stock Out"
            else:
                stock_status = "In Stock"
                product_is_stock_out = False

            variants_with_stock.append({
                'variant': var,
                'stock_status': stock_status
            })


        # offer
        productoffer=ProductOffer.objects.filter(product=p,product__product_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')
        brandoffer=BrandOffer.objects.filter(brand=p.brand,brand__brand_status="published",is_active=True,start_date__lte=timezone.now(),end_date__gte=timezone.now()).order_by('-discount_percentage')
    
        offer=None
        discounted_price = p.price
        if productoffer and brandoffer:
            if productoffer[0].discount_percentage<brandoffer[0].discount_percentage:
                offer=brandoffer[0]
                discounted_price = offer.apply_discount(p.price)
            else:
                offer=productoffer[0]
                discounted_price = offer.apply_discount(p.price)
        elif productoffer:
            offer=productoffer[0]
            discounted_price = offer.apply_discount(p.price)
        elif brandoffer:
            offer=brandoffer[0]
            discounted_price = offer.apply_discount(p.price)

        product_offer.append({
            'product':p,
            'offer':offer,
            'discounted_price':discounted_price,
            'product_is_stock_out': product_is_stock_out,
            'variants_with_stock': variants_with_stock,
            
        })

    
    context={
        "products":products,
        'offer1':offer1,
        'discounted_price1':discounted_price1,
        "variant_colour":variant_colour,
        "variant_size":variant_size,
        "variant_image":variant_image,
        "product_offer":product_offer,
        'product_is_stock_out': product_is_stock_out,  
        'variant_is_stock_out': variant_is_stock_out,  
        'size_is_stock_out': size_is_stock_out, 
        'reviews' : reviews,
        'avg_rating':avg_rating,
        'double_avg_rating':double_avg_rating,
        'rating_distribution':rating_distribution,
        'make_review':make_review
    }
    
    return render(request,"product.html",context)

# reviwadd
@login_required(login_url="user-login")
def ajax_add_review(request,id):
    user=request.user
    review=request.POST.get("review")
    rating=request.POST.get("rating")
    product=Product.objects.get(id=id)

    review=Review.objects.create(user=user,review=review,product=product,rating=rating)
    average_rating=Review.objects.filter(product__id=id).aggregate(rating=Avg('rating'))
    context={
        'user':user.username,
        'review':request.POST.get("review"),
        'rating':request.POST.get("rating")

    }
    return JsonResponse({
        'bool':True,
        'context':context,
        'average_rating':average_rating
    })
    

# reviewfunction
def get_reviews_by_product(product_id):
    # all reviews
    reviews=Review.objects.filter(product__id=product_id).order_by("-date")
    # getting avg
    average_rating=Review.objects.filter(product__id=product_id).aggregate(rating=Avg('rating'))

   
    # ratingbar
    total_reviews=reviews.count()
    rating_distribution={str(i):0 for i in range(1,6)}

    if total_reviews>0:
        rating_counts = reviews.values('rating').annotate(count=Count('rating')).order_by('rating')

        for item in rating_counts:
            rating_distribution[str(item['rating'])]=round((item['count']/total_reviews)*100)

    if average_rating['rating'] is not None:
        double_avg_rating = 20 * round(average_rating['rating'])  # Use round for better precision
    else:
        double_avg_rating = 0
    return reviews,average_rating,double_avg_rating,rating_distribution


def get_variant_images(request,id):
    
    variant_images =  VariantImages.objects.filter(variant__id = id)
    data = list(variant_images.values())
    return JsonResponse(data, safe=False)

    
def get_variant_sizes(request,id):
    
    variant_sizes =  VariantSize.objects.filter(variant__id = id,size_status="published",stock="stock_in")
    data = list(variant_sizes.values())
    return JsonResponse(data, safe=False)


# filter data
def filter_data(request):
    category = request.GET.getlist('category[]')
    brand = request.GET.getlist('brand[]')
    colour = request.GET.getlist('colour[]')
    size = request.GET.getlist('size[]')
    price = request.GET.getlist('price[]')

    products = Product.objects.filter(product_status="published")
    
    # Price filtering
    q_objects = Q()
    for price_range in price:
        if '-' in price_range: 
            min_price, max_price = map(int, price_range.split("-"))
            q_objects |= Q(discounted_price__gte=min_price, discounted_price__lte=max_price)
        else:  
            min_price = int(price_range)
            q_objects |= Q(discounted_price__gte=min_price)
    
    if q_objects:
        products = products.filter(q_objects)

    # Category, Brand, Colour, and Size filtering
    if category:
        products = products.filter(category__id__in=category)
    if brand:
        products = products.filter(brand__id__in=brand)
    if colour:
        products = products.filter(indproduct__id__in=colour)
    if size:
        products = products.filter(indproduct__variant__id__in=size)

    product_offer = []

    for p in products:
        # Stock check
        product_is_stock_out = True
        variants_with_stock = []

        for var in p.indproduct.filter(variant_status="published"):
            if var.is_stock_out():
                stock_status = "Stock Out"
            else:
                stock_status = "In Stock"
                product_is_stock_out = False

            variants_with_stock.append({
                'variant': var,
                'stock_status': stock_status
            })

        # Offer check
        productoffer = ProductOffer.objects.filter(
            product=p, product__product_status="published", is_active=True,
            start_date__lte=timezone.now(), end_date__gte=timezone.now()
        ).order_by('-discount_percentage')

        brandoffer = BrandOffer.objects.filter(
            brand=p.brand, brand__brand_status="published", is_active=True,
            start_date__lte=timezone.now(), end_date__gte=timezone.now()
        ).order_by('-discount_percentage')

        offer = None
        discounted_price = p.price
        if productoffer and brandoffer:
            if productoffer[0].discount_percentage < brandoffer[0].discount_percentage:
                offer = brandoffer[0]
                discounted_price = offer.apply_discount(p.price)
            else:
                offer = productoffer[0]
                discounted_price = offer.apply_discount(p.price)
        elif productoffer:
            offer = productoffer[0]
            discounted_price = offer.apply_discount(p.price)
        elif brandoffer:
            offer = brandoffer[0]
            discounted_price = offer.apply_discount(p.price)

        product_offer.append({
            'product': p,
            'offer': offer,
            'discounted_price': discounted_price,
            'product_is_stock_out': product_is_stock_out,
            'variants_with_stock': variants_with_stock
        })

    context = {
        "product_offer": product_offer,
        "category": Category.objects.filter(category_status="published").exclude(parent=None),
        "size": VariantSize.objects.filter(size_status="published").distinct("size"),
        "variant": Variant.objects.filter(variant_status="published").distinct("colour"),
        "brand": Brand.objects.filter(brand_status="published")
    }

    return render(request, 'jsproductlist.html', context)




def add_to_cart(request):
    product_id = request.GET.get('id')
    color_variant_id = request.GET.get('color_variant')
    size_variant_id = request.GET.get('size_variant')
    qty = int(request.GET.get('qty'))
    price = float(request.GET.get('price'))
    # image = request.GET.get('image')
    product = get_object_or_404(Product, id=product_id)
    color_variant = Variant.objects.filter(product__id=product_id,id=color_variant_id).first()
    size_variant = VariantSize.objects.filter(size=size_variant_id,variant__id=color_variant_id,variant__product__id=product_id).first()
    image_url=VariantImages.objects.filter(variant__id=color_variant_id,variant__product__id=product_id).first()

    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if request.session.session_key:
            session_key = request.session.session_key or request.session.create()
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)


    # cart craeted or get
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        color_variant=color_variant,
        size_variant=size_variant,
        image=image_url,
        defaults={'quantity': qty, 'price': price}
    )
    if not created:
        cart_item.quantity += qty
        cart_item.save()
    return JsonResponse({'message': 'Item added to cart successfully','totalitems': cart.items.count()})


@never_cache
def cart(request):
    if request.user.is_authenticated:
        # if cart.items.size_variant.stock=="stock_in"
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)

    # Get items in the cart
    cart_items = cart.items.filter(product__product_status="published",size_variant__size_status="published",size_variant__stock="stock_in").order_by('id') if cart else []
    discounted_price = request.session.get('discounted_price', None)
    if discounted_price is not None:  # Check if the key exists
        request.session.pop('discounted_price')
    # Check if original prices are saved in session
    original_prices = request.session.get('original_prices', None)
    if original_prices:
            # Restore the original prices from the session
        for item in cart_items:
            if str(item.id) in original_prices:  # Ensure matching ID as a string
                item.price = Decimal(original_prices[str(item.id)])  # Convert back to Decimal
                item.save()

            # Safely clear the session values after restoring prices
        if 'original_prices' in request.session:
            del request.session['original_prices']

    # total items and total amount
    total_items = cart_items.count()
    subtotal_amount = sum(item.total_price() for item in cart_items)
    request.session['total_items']=total_items
    shipping_charge = 0 if subtotal_amount == 0 else 50
    total_amount=subtotal_amount+shipping_charge
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    context = {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_amount': total_amount,
        'shipping_charge':shipping_charge,
        'subtotal_amount':subtotal_amount,
        'message' : message,
        'message_type':message_type
    }
    return render(request, "cart.html", context)


def delete_cart_item(request):
    cart_item_id = request.GET.get('id')
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(id=cart_item_id,cart__user=request.user)
        
    else:
        session_key = request.session.session_key
        cart_item = CartItem.objects.filter(id=cart_item_id,cart__session_key=session_key)
    
    cart_item.delete()
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()

    cart_items = cart.items.filter(product__product_status="published",size_variant__size_status="published").order_by('id') if cart else []
    total_items = cart_items.count()
    subtotal_amount = sum(item.total_price() for item in cart_items)
    shipping_charge = 0 if subtotal_amount == 0 else 50
    total_amount=subtotal_amount+shipping_charge
    context={
        'message': 'Item removed from cart successfully',
        'cart_items': cart_items,
        'total_items': total_items,
        'subtotal_amount': subtotal_amount,
        'total_amount':total_amount,
        'shipping_charge':shipping_charge,
        }
    t = render_to_string('jscartdelete.html',context)
    return JsonResponse({'data': t})


def update_cart_item(request):
    cart_item_id = request.GET.get('id')
    qty = int(request.GET.get('qty'))

    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.quantity = qty
    cart_item.save()
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()

    cart_items = cart.items.filter(product__product_status="published",size_variant__size_status="published") if cart else []
    total_items = cart_items.count()
    subtotal_amount = sum(item.total_price() for item in cart_items)
    shipping_charge = 0 if subtotal_amount == 0 else 50
    total_amount=subtotal_amount+shipping_charge
    
    context={
        'message': 'Cart updated successfully',
        'cart_items': cart_items,
        'total_items': total_items,
        'subtotal_amount':subtotal_amount,
        'total_amount': total_amount,
        'shipping_charge':shipping_charge,
        }

    t = render_to_string('jscartdelete.html',context)
    return JsonResponse({'data': t})

    
def Account(request):
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "message": message,
        "message_type": message_type,
    }
    return render(request, "Myaccount.html", context)

@never_cache
@login_required(login_url="user-login")
def Editprofile(request,id):
    user=User.objects.get(id=id)
    if request.method=="POST":
        username = request.POST.get('username')
        phone = request.POST.get('phone')

        required_fields = [username,phone]
        if any(field.strip() == "" for field in required_fields):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect(f"/editprofile/{id}")
        try:
            user.username=username
            user.phoneno = phone
            user.save()
            request.session['message'] = "profile updated successfully!"
            request.session['message_type'] = "success"
            return redirect("account")
        except Exception as e:
            request.session['message'] = f"An error occurred: {str(e)}"
            request.session['message_type'] = "danger"
            return redirect(f"/editprofile/{id}")
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "user":user,
        "message": message,
        "message_type": message_type,
    }  
    return render(request, "editprofile.html", context)

@login_required(login_url="user-login")
@never_cache
def Addaddress(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        required_fields = [first_name, last_name, street, city, state, postal_code, country, phone, email]
        if any(field.strip() == "" for field in required_fields):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect("addaddress")
        
        try:
            ShippingAddress.objects.create(
                user=user,first_name=first_name,last_name=last_name,street=street,city=city,state=state,postal_code=postal_code,country=country,phone=phone,email=email
            )
            request.session['message'] = "Address added successfully!"
            request.session['message_type'] = "success"
            return redirect("addaddress")
        except Exception as e:
            request.session['message'] = f"An error occurred: {str(e)}"
            request.session['message_type'] = "danger"
            return redirect("addaddress")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "message": message,
        "message_type": message_type,
    }
    return render(request, "addaddress.html", context)

@login_required(login_url="user-login")
def Editaddress(request,id):
    address=ShippingAddress.objects.get(id=id)
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        required_fields = [first_name, last_name, street, city, state, postal_code, country, phone, email]
        if any(field.strip() == "" for field in required_fields):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect(f"/editaddress/{id}")
        
        try:
            address.first_name = first_name
            address.last_name = last_name
            address.street = street
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.country = country
            address.phone = phone
            address.email = email
            address.save()
            request.session['message'] = "Address updated successfully!"
            request.session['message_type'] = "success"
            return redirect("address")
        except Exception as e:
            request.session['message'] = f"An error occurred: {str(e)}"
            request.session['message_type'] = "danger"
            return redirect(f"/editaddress/{id}")

    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "address":address,
        "message": message,
        "message_type": message_type,
    }
    return render(request, "editaddress.html", context)

def Delete_address(request,id):
    address=ShippingAddress.objects.get(id=id)
    address.delete()
    request.session['message'] = "Address deleted successfully!"
    request.session['message_type'] = "success"
    return redirect("address")

def Address(request):
    address=ShippingAddress.objects.filter(user=request.user)
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "address":address,
        "message": message,
        "message_type": message_type,
        
    }
    return render(request, "address.html",context)


@login_required(login_url="user-login")
@never_cache
def Checkout(request):
    user=request.user
    cart=Cart.objects.get(user=user)
    cart_items = cart.items.filter(product__product_status="published",size_variant__size_status="published",size_variant__stock="stock_in").order_by('id') if cart else []
    subtotal_price = sum(item.total_price() for item in cart_items)
    shipping_charge = 0 if subtotal_price == 0 else 50
    total_price=subtotal_price+shipping_charge
    
     # Check stock
    for cart_item in cart_items:
        if cart_item.size_variant:
            size_variant = VariantSize.objects.filter(
                variant__product__title=cart_item.product.title,  
                variant__colour=cart_item.color_variant,  
                size=cart_item.size_variant.size  
            ).first()  

            if size_variant and cart_item.quantity > size_variant.quantity: 
                request.session['message'] = f"Insufficient stock for {cart_item.product.title} (Size: {cart_item.size_variant.size}).(Requested: {cart_item.quantity}, Available: {size_variant.quantity}). Please reduce the quantity."
                request.session['message_type'] = "danger"
                return redirect("cart") 

    address=ShippingAddress.objects.filter(user=request.user)
    if not address.exists():
        return redirect("addaddress")
    
    # coupon adding 
    discounted_price = request.session.get('discounted_price', None)
    coupon= request.session.get('coupon', None)
    discountapplied = Decimal(request.session.get('discount', 0))
    discount=0
    if discounted_price is not None:
        discount=discountapplied
        subtotal_price = Decimal(discounted_price)
        total_price=subtotal_price+shipping_charge


    if request.method=="POST":
        payment_method=request.POST.get("payment_method")
        address_id=request.POST.get("id")
        

        if not all([address_id,payment_method]):
            request.session['message'] = "All fields are required."
            request.session['message_type'] = "warning"
            return redirect("checkout") 

        try:
            shipping_address = ShippingAddress.objects.get(id=address_id)
            first_name=shipping_address.first_name
            last_name=shipping_address.last_name
            street=shipping_address.street
            city = shipping_address.city
            state = shipping_address.state
            country = shipping_address.country
            postal_code= shipping_address.postal_code
            phone = shipping_address.phone
            email = shipping_address.email

        except (ShippingAddress.DoesNotExist) as e:
            request.session['message'] = f"Invalid selection for {str(e).split()[0]}."
            request.session['message_type'] = "danger"
            return redirect("checkout")

        if total_price==0:
            request.session['message'] = "your cart is empty"
            request.session['message_type'] = "danger"
            return redirect("checkout")

        if payment_method=="Cash on Delivery":
            if total_price>1000:
                request.session['message'] = "Cash on Delivery is unavailable for orders exceeding ₹1000. Please choose an alternate payment method."
                request.session['message_type'] = "warning"
                return redirect('checkout')
            order = Cart_Order.objects.create(
                user=user,
                total_price=total_price,
                payment_method=payment_method,
                first_name = first_name,
                last_name =last_name,
                street=street,
                city = city,
                state=state,
                postal_code=postal_code,
                country=country,
                phone=phone,
                email=email,
                discount=discount,
            )

            
            # request.session.pop('discounted_price',None)
        
        elif payment_method=="wallet":
            wallet=Wallet.objects.filter(user=request.user).first()
            if not wallet:
                request.session['message'] = "No wallet found for your account."
                request.session['message_type'] = "warning"
                return redirect('checkout') 

            if total_price>wallet.balance:
                request.session['message'] = "total amount is greater than your wallet balance"
                request.session['message_type'] = "warning"
                return redirect('checkout')
            else:
                wallet.balance-=total_price
                wallet.save()
                order = Cart_Order.objects.create(
                    user=user,
                    total_price=total_price,
                    payment_method=payment_method,
                    paid_status=True,
                    first_name = first_name,
                    last_name =last_name,
                    street=street,
                    city = city,
                    state=state,
                    postal_code=postal_code,
                    country=country,
                    phone=phone,
                    email=email,
                    discount=discount,
                )

        elif payment_method=="Razorpay":
            try:
                # create razorpay client
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

                # create order
                order_data = {
                "amount": int(total_price * 100),  # Amount in paisa (1 INR = 100 paisa)
                "currency": "INR",
                "payment_capture": "1" 
                }
                razorpay_order = client.order.create(data=order_data)
                order_id = razorpay_order['id']

                # Create the order
                order = Cart_Order.objects.create(
                    user=user,
                    total_price=total_price,
                    payment_method="razorpay",
                    razorpay_order_id=order_id,
                    paid_status=False,
                    first_name = first_name,
                    last_name =last_name,
                    street=street,
                    city = city,
                    state=state,
                    postal_code=postal_code,
                    country=country,
                    phone=phone,
                    email=email,
                    discount=discount,

                )
                # Create order items
                for cart_item in cart_items:
                    OrderItems.objects.create(
                        order=order,
                        product=cart_item.product.title,
                        image=cart_item.image.image.url if cart_item.image else "",
                        colour=cart_item.color_variant if cart_item.color_variant else "",
                        size=cart_item.size_variant if cart_item.size_variant else "",
                        qty=cart_item.quantity,
                        price=cart_item.price,
                        total=cart_item.total_price()
                    )

                    if cart_item.size_variant:
                        size_variant = VariantSize.objects.filter(
                            variant__product__title=cart_item.product.title,
                            variant__colour=cart_item.color_variant,
                            size=cart_item.size_variant
                        ).first()
                        if size_variant:
                            size_variant.quantity -= cart_item.quantity  
                            size_variant.save()  
                        else:
                            raise ValueError("Selected size variant does not exist or insufficient stock.")
                if discounted_price is not None:
                    coupon=Coupon.objects.get(code=coupon)
                    couponusage = CouponUsage.objects.create(coupon=coupon,user=user)
                    coupon.used_count+=1
                    coupon.save()
                # Clear the cart 
                # cart.items.all().delete()
                return render(request, "razerpayment.html", {
                    "order": order,
                    "order_id": razorpay_order['id'],
                    "total_price": int(total_price * 100),
                    "razorpay_merchant_key": settings.RAZORPAY_KEY_ID,
                    "address_id": address_id,
                    
                })

            except Exception as e:
                request.session['message'] = f"Razorpay error: {str(e)}"
                request.session['message_type'] = "danger"
                return redirect("checkout")

        else:
            request.session['message'] = "Invalid payment method."
            request.session['message_type'] = "warning"
            return redirect("checkout")


        # Create OrderItems for each cart item
        for cart_item in cart_items:
            OrderItems.objects.create(
                order=order,
                product=cart_item.product.title,  
                image=cart_item.image.image.url if cart_item.image else "",
                colour=cart_item.color_variant if cart_item.color_variant else "",
                size=cart_item.size_variant if cart_item.size_variant else "",
                qty=cart_item.quantity,
                price=cart_item.price,
                total=cart_item.total_price()
            )

            if cart_item.size_variant:
                    size_variant = VariantSize.objects.filter(
                        variant__product__title=cart_item.product.title,
                        variant__colour=cart_item.color_variant,
                        size=cart_item.size_variant
                    ).first()
                    if size_variant:
                        size_variant.quantity -= cart_item.quantity  # Assuming `stock` is the field name
                        size_variant.save()  # Save changes to the database
                       
                    else:
                        raise ValueError("Selected size variant does not exist or insufficient stock.")
                    
        if discounted_price is not None:
            coupon=Coupon.objects.get(code=coupon)
            couponusage = CouponUsage.objects.create(coupon=coupon,user=user)
            coupon.used_count+=1
            coupon.save()
        # Clear the cart
        # cart.items.all().delete()
        return redirect("order_success")
    
    active_coupons = Coupon.objects.filter(active=True)
    used_coupons = CouponUsage.objects.filter(user=user).values_list('coupon', flat=True)
    available_coupons = active_coupons.exclude(id__in=used_coupons).filter(start_date__lte=date.today(),  end_date__gte=date.today(), used_count__lt=F('usage_limit') )
    
    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)
    context = {
        "address":address,
        "message": message,
        "message_type": message_type,
        'cart_items': cart_items,
        'total_price': total_price,
        'subtotal_price': subtotal_price,
        
        'shipping_charge': shipping_charge,
        'available_coupons' : available_coupons,
        'discount' : discount,
       
    }
    return render(request, "checkout.html",context)


# razerpay payment varification
@csrf_exempt  
def verify_payment(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")
       
        try:
            #Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

           
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)
            
            order = Cart_Order.objects.get(razorpay_order_id=order_id)
            order.paid_status = True
            order.razorpay_payment_id= payment_id
            order.razorpay_signature= signature
            order.save()
            cart=Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return JsonResponse({"status": "Payment Verified", "redirect": "/order_success/"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        # return an error if method is not post
        return JsonResponse({"error": "Invalid request method. Only POST is allowed."}, status=405)

# retry
def Retry(request,id):
    order=get_object_or_404(Cart_Order, id=id) 
    orderitems=OrderItems.objects.filter(order__id=id)
    try:
        # create razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        # create order
        order_data = {
        "amount": int(order.total_price * 100),  # Amount in paisa (1 INR = 100 paisa)
        "currency": "INR",
        "payment_capture": "1" 
        }
        razorpay_order = client.order.create(data=order_data)
        order_id = razorpay_order['id']

        # Create the order
        order = order
        order.razorpay_order_id=order_id
        order.save()
        return render(request, "razerpayment.html", {
            "order": order,
            "order_id": razorpay_order['id'],
            "total_price": int(order.total_price * 100),
            "razorpay_merchant_key": settings.RAZORPAY_KEY_ID,
        })

    except Exception as e:
        request.session['message'] = f"Razorpay error: {str(e)}"
        request.session['message_type'] = "danger"
        return redirect("order")
    

@never_cache
def Order_success(request):
    return render(request,"OrderSuccess.html")
    

# order details
@login_required(login_url="user-login")
def Order_details(request):
    user=request.user
    orders=Cart_Order.objects.filter(user=user).order_by('-id')

    # for order in orders:
    #     if order.total_price<=50 and not order.paid_status:
    #         order.status="cancelled"
    #         order.total_price = 0
    #         order.save()
       
    context={
        "orders":orders,
        "message": request.session.pop("message", None),
        "message_type": request.session.pop("message_type", None),
    }
    return render(request,"order.html",context)

# orderview
@login_required(login_url="user-login")
def Order_items(request, id):
    
    order=Cart_Order.objects.get(id=id)
    orderitems=OrderItems.objects.filter(order__id=id)
    
    subtotal=0
    for item in orderitems:
        subtotal+=item.price*item.qty
    shipping_charge = 0 if subtotal == 0 else 50
    
    for item in orderitems:
        if item.refund_status == 'Refunded' and not item.refund_processed:
            refund_amount = Decimal(item.price) * item.qty  # Assume the refund amount is based on item price
            item.refund_amount=refund_amount
            item.save()

            item_total_price = Decimal(item.total)  # Ensure this is Decimal
            order.total_price -= item_total_price
            order.save()
        
          
            # Add the refund to the user's wallet
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance = Decimal(wallet.balance) + refund_amount # Add refund amount to the wallet
            wallet.save()
            item.refund_processed = True
            item.save()
    
    #check all items are cancelled
    all_cancelled = True
    all_returned = True
    for item in orderitems:
        if item.cancel_status != 'Cancelled':  
            all_cancelled = False
            break  

    # check all items are returned
    for item in orderitems:
        if item.return_status != 'Returned':  
            all_returned = False
            break    
    if all_cancelled and not order.paid_status:
        order.status = 'cancelled'
        order.total_price=0  
        order.save()
    elif all_cancelled:
        order.status = 'cancelled'  
        order.save()
    elif all_returned:
        order.status = 'Returned'  
        order.save()
    
    context = {
        "order": order,
        "orderitems": orderitems,
        "message": request.session.pop("message", None),
        "message_type": request.session.pop("message_type", None),
        "subtotal":subtotal,
        "shipping_charge":shipping_charge
    }
    return render(request, "orderitems.html",context)

@login_required(login_url="user-login")
def cancel_item(request,item_id):
    item = get_object_or_404(OrderItems, id=item_id)
    if item.order.payment_method=="Cash on Delivery":
        if item.cancel_status == 'Not Cancelled':
            item.cancel_item()
            item.refund_amount=item.price
            item.save()
            item_total_price = Decimal(item.total)  # Ensure the price is Decimal
            item.order.total_price -= item_total_price
            item.order.save()

            # increase quantity
            if item.size:
                variant_size = VariantSize.objects.filter(
                    variant__colour=item.colour, size=item.size, variant__product__title=item.product
                ).first()  
               
                if variant_size:
                    variant_size.quantity += item.qty
                    variant_size.save()
                    
            request.session['message'] = "your order is cancelled"
            request.session['message_type'] = "danger"
            return redirect(f'/orderitems/{item.order.id}/')
    else:
        try:
            if item.cancel_status == 'Not Cancelled':
                item.cancel_item()
                return process_refund_and_add_to_wallet(request, item_id)
                
            else:
                request.session['message'] = "This item has already been canceled"
                request.session['message_type'] = "warning"
                return redirect(f'/orderitems/{item.order.id}/')
        except Exception as e:
            request.session['message'] = f"An error occurred: {str(e)}"
            request.session['message_type'] = "danger"
            return redirect(f'/orderitems/{item.order.id}/')

    context={
        "message": request.session.pop("message", None),
        "message_type": request.session.pop("message_type", None),
    }
    return render (request, "orderitems.html",context)


def return_item(request, item_id):
    item = get_object_or_404(OrderItems, id=item_id)

    try:
        if item.return_status == 'Not Returned':
            item.return_item()
            return process_refund_and_add_to_wallet(request, item_id)
            
        else:
            request.session['message'] = "This item has already been returned"
            request.session['message_type'] = "warning"
            return redirect(f'/orderitems/{item.order.id}/')
    except Exception as e:
        request.session['message'] = f"An error occurred: {str(e)}"
        request.session['message_type'] = "danger"
        return redirect(f'/orderitems/{item.order.id}/')

    context={
        "message": request.session.pop("message", None),
        "message_type": request.session.pop("message_type", None),
    }
    return render (request, "orderitems.html",context)

def process_refund_and_add_to_wallet(request, item_id):
    item = get_object_or_404(OrderItems, id=item_id)
    
    try:
        if item.refund_status == 'processing' and item.return_status == 'Returned':
            # increase quantity
            if item.size:
                variant_size = VariantSize.objects.filter(
                    variant__colour=item.colour, size=item.size, variant__product__title=item.product
                ).first()  # Use first() to ensure only one result is returned
               
                if variant_size:
                    variant_size.quantity += item.qty
                    variant_size.save()
                else:
                    # If no matching variant size, log an error or handle it
                    request.session['message'] = "Variant size not found for update."
                    request.session['message_type'] = "danger"
                    return redirect(f'/orderitems/{item.order.id}/')
            request.session['message'] = "Return is processing"
            request.session['message_type'] = "warning"
            return redirect(f'/orderitems/{item.order.id}/')
        
        elif item.refund_status == 'processing' and item.cancel_status == 'Cancelled':
            # increase quantity
            if item.size:
                variant_size = VariantSize.objects.filter(
                    variant__colour=item.colour, size=item.size, variant__product__title=item.product
                ).first()  # Use first() to ensure only one result is returned
                if variant_size:
                    variant_size.quantity += item.qty
                    variant_size.save()
                else:
                    # If no matching variant size, log an error or handle it
                    request.session['message'] = "Variant size not found for update."
                    request.session['message_type'] = "danger"
                    return redirect(f'/orderitems/{item.order.id}/')
            request.session['message'] = "your order is cancelled"
            request.session['message_type'] = "warning"
            return redirect(f'/orderitems/{item.order.id}/')
        
        elif item.return_status != 'Returned':
            # If the item has not been returned yet, show a warning
            request.session['message'] = "Return is processing"
            request.session['message_type'] = "warning"
            return redirect(f'/orderitems/{item.order.id}/')

        else:
            # If the refund has already been processed, show a warning
            request.session['message'] = "This item has already been refunded."
            request.session['message_type'] = "warning"
            return redirect(f'/orderitems/{item.order.id}/')

    except Exception as e:
        # Handle any unexpected errors during refund processing
        request.session['message'] = f"An error occurred: {str(e)}"
        request.session['message_type'] = "danger"
        return redirect(f'/orderitems/{item.order.id}/')

def return_confirmation(request):
    refund_amount = request.session.get('refund_amount', 0)  # Default to 0 if not available
    orderitem_id = request.session.get('orderitemid', None) 
    order_id = request.session.get('orderid', None) 
    context={
        'refund_amount':refund_amount,
        'orderitem_id':orderitem_id,
        'order_id':order_id
    }
    return render(request, 'return_confirmation.html',context)

def Orderitem_view(request, order_id):

    order = get_object_or_404(OrderItems, id=order_id)
        
    context = {
        'order':order
    }
    
    # Pass the order object to the template
    return render(request, 'orderview.html',context)

# invoice download
def Invoice_Download(request, id):
    # Fetch the order item based on the provided ID
    orderitem = OrderItems.objects.get(id=id)
    order = orderitem.order  # Access the associated order of this item

    # Create an HTTP response with the appropriate PDF header
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Order_Item_Report_{orderitem.id}.pdf"'

    # Initialize the PDF canvas
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50  # Initial y-position for the content

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y, f"Order Item Report")
    y -= 40

    # Order details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Order ID: {order.id}")
    pdf.drawString(300, y, f"Date: {order.created_at.strftime('%Y-%m-%d')}")
    y -= 20
    pdf.drawString(50, y, f"Customer: {order.first_name} {order.last_name}")
    pdf.drawString(300, y, f"Invoice No: {orderitem.invoice_no}")
    y -= 40

    
    # Table Header for Order Items
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Product")
    pdf.drawString(250, y, "Quantity")
    pdf.drawString(350, y, "Price")
    pdf.drawString(450, y, "Total")
    y -= 20
    pdf.line(50, y, 550, y)  # Add a line under the table header
    y -= 20

    # Table Content for Order Items
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, orderitem.product)  # Assuming 'name' is the field for product name
    pdf.drawString(250, y, str(orderitem.qty))
    pdf.drawString(350, y, f"{orderitem.price:.2f}")
    pdf.drawString(450, y, f"{orderitem.qty * orderitem.price:.2f}")
    y -= 20

    # Add a new page if content goes beyond current page
    if y < 50:
        pdf.showPage()
        y = height - 50

    # Order Status Section
    pdf.setFont("Helvetica-Bold", 12)
    y -= 20
    if order.status == 'delivered' or order.status == 'Returned':
        if orderitem.return_status == 'Returned':
            if orderitem.refund_status == 'Refunded':
                pdf.drawString(50, y, "Refund Status: This product has been refunded.")
                y -= 20
                pdf.drawString(50, y, "Check your wallet for refund details.")
            elif orderitem.refund_status == 'processing':
                pdf.drawString(50, y, "Refund Status: Refund is processing and will be completed within 7 working days.")
            else:
                pdf.drawString(50, y, "The product has been returned, but the refund status is not updated yet.")
        elif orderitem.cancel_status == 'Cancelled':
            pdf.drawString(50, y, "Your order item has been cancelled. Product is eligible for refund based on its status.")
        else:
            pdf.drawString(50, y, "Return Status: Your order item was delivered.")
    elif order.status == 'processing' or order.status == 'cancelled':
        if orderitem.cancel_status == 'Cancelled':
            if orderitem.refund_status == 'Refunded':
                pdf.drawString(50, y, "Your product is cancelled. Refund Status: This product has been refunded.")
            elif orderitem.refund_status == 'processing' and order.paid_status:
                pdf.drawString(50, y, "Your product is cancelled. Refund is processing.")
            else:
                pdf.drawString(50, y, "The product has been cancelled.")
        else:
            pdf.drawString(50, y, "Your order item is being processed.")
    else:
        pdf.drawString(50, y, f"Your order status is: {order.status}")
    y -= 40

    # Shipping Address Section
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Shipping Address:")
    y -= 20
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"{order.first_name} {order.last_name}")
    y -= 20
    pdf.drawString(50, y, f"{order.street}, {order.city}, {order.state}, {order.country}")
    y -= 20
    pdf.drawString(50, y, f"Postal Code: {order.postal_code}")
    y -= 20
    pdf.drawString(50, y, f"Phone: {order.phone}")
    y -= 40

    # Footer with generation timestamp
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, 30, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save and return the PDF
    pdf.save()
    return response




def Cancel_Order(request,id):
    order=get_object_or_404(Cart_Order, id=id) 
    orderitems=OrderItems.objects.filter(order__id=id)
    
    for item in orderitems:
        if item.cancel_status!="Cancelled":
            item.cancel_item()
            if item.size:
                variant_size = VariantSize.objects.filter(
                    variant__colour=item.colour, size=item.size, variant__product__title=item.product
                ).first()  # Use first() to ensure only one result is returned
                if variant_size:
                    variant_size.quantity += item.qty
                    variant_size.save()
                else:
                    # If no matching variant size, log an error or handle it
                    request.session['message'] = "Variant size not found for update."
                    request.session['message_type'] = "danger"
                    return redirect(f'/orderitems/{item.order.id}/')
    order.status="cancelled"
    order.save()
    if order.paid_status==True:
        request.session['message'] = "Your order has been cancelled. The refund is currently being processed and will be credited to your account shortly."
        request.session['message_type'] = "success"
    else:
        request.session['message'] = "Your order has been cancelled."
        request.session['message_type'] = "success"
    return redirect('order')

def Return_Order(request,id):
    order=get_object_or_404(Cart_Order, id=id) 
    orderitems=OrderItems.objects.filter(order__id=id)
    for item in orderitems:
        item.return_item()
        # increase quantity
        if item.size:
            variant_size = VariantSize.objects.filter(
                variant__colour=item.colour, size=item.size, variant__product__title=item.product
            ).first()  # Use first() to ensure only one result is returned
            if variant_size:
                variant_size.quantity += item.qty
                variant_size.save()
            else:
                # If no matching variant size, log an error or handle it
                request.session['message'] = "Variant size not found for update."
                request.session['message_type'] = "danger"
                return redirect(f'/orderitems/{item.order.id}/')
    order.status="Returned"
    order.save()
    request.session['message'] = "Your order has been returned. The refund is currently being processed and will be credited to your account shortly."
    request.session['message_type'] = "success"
    return redirect('order')


def My_wallet(request):
    user=request.user
    wallet=Wallet.objects.filter(user=user)
    context={
        'wallet':wallet,
    }
    return render(request,'mywallet.html',context)


# wishlist
def add_to_wishlist(request):
    product_id = request.GET.get('id')
    color_variant_id = request.GET.get('color_variant')
    size_variant_id = request.GET.get('size_variant')
    qty = int(request.GET.get('qty'))
    price = float(request.GET.get('price'))
    # image = request.GET.get('image')

    product = get_object_or_404(Product, id=product_id)
    color_variant = Variant.objects.filter(product__id=product_id,id=color_variant_id).first()
    size_variant = VariantSize.objects.filter(size=size_variant_id,variant__id=color_variant_id,variant__product__id=product_id).first()
    image_url=VariantImages.objects.filter(variant__id=color_variant_id,variant__product__id=product_id).first()

    # Check if user is authenticated
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    else:
        if request.session.session_key:
            session_key = request.session.session_key or request.session.create()
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        wishlist, created = Wishlist.objects.get_or_create(session_key=session_key, user=None)


    # Check if item already exists
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
        color_variant=color_variant,
        size_variant=size_variant,
        image=image_url,
        defaults={'quantity': qty, 'price': price}
    )
    if not created:
        wishlist_item.quantity += qty
        wishlist_item.save()
    return JsonResponse({'message': 'Item added to wishlist successfully','totalitems': wishlist.wishlist_items.count()})

def wishlist(request):
    if request.user.is_authenticated:
        # if cart.items.size_variant.stock=="stock_in"
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        wishlist, _ = Wishlist.objects.get_or_create(session_key=session_key, user=None)
    
    wishlist_items = wishlist.wishlist_items.filter(product__product_status="published",size_variant__size_status="published").order_by('id') if cart else []

    wishlist_items_with_stock_status = []
    for item in wishlist_items:
        size_stock_status = "In Stock" if item.size_variant and item.size_variant.stock == "stock_in" else "Out of Stock"
        # color_stock_status = "In Stock" if item.color_variant and item.color_variant.stock == "stock_in" else "Out of Stock"
        
        wishlist_items_with_stock_status.append({
            'item': item,
            'size_stock_status': size_stock_status,
            # 'color_stock_status': color_stock_status,
        })

    total_item = len(wishlist_items_with_stock_status)
    request.session['total_item']=total_item
    
    context = {
        'wishlist_items_with_stock_status': wishlist_items_with_stock_status,
        'total_items': total_item,
    }
    return render(request,"wishlist.html",context)


def delete_wishlist_item(request):
    wishlist_item_id = request.GET.get('id')
    if request.user.is_authenticated:
        wishlist_item = WishlistItem.objects.filter(id=wishlist_item_id,wishlist__user=request.user)
        
    else:
        session_key = request.session.session_key
        wishlist_item = WishlistItem.objects.filter(id=wishlist_item_id,wishlist__session_key=session_key)
    
    wishlist_item.delete()

    if request.user.is_authenticated:
        # if cart.items.size_variant.stock=="stock_in"
        wishlist= Wishlist.objects.get(user=request.user)
    else:
        session_key = request.session.session_key
        wishlist= Wishlist.objects.filter(session_key=session_key).first()
    
    wishlist_items = wishlist.wishlist_items.filter(product__product_status="published",size_variant__size_status="published").order_by('id') if cart else []

    wishlist_items_with_stock_status = []
    for item in wishlist_items:
        size_stock_status = "In Stock" if item.size_variant and item.size_variant.stock == "stock_in" else "Out of Stock"
        # color_stock_status = "In Stock" if item.color_variant and item.color_variant.stock == "stock_in" else "Out of Stock"
        
        wishlist_items_with_stock_status.append({
            'item': item,
            'size_stock_status': size_stock_status,
            # 'color_stock_status': color_stock_status,
        })

    total_items = len(wishlist_items_with_stock_status)
    
    context = {
        'wishlist_items_with_stock_status': wishlist_items_with_stock_status,
        'total_items': total_items,
    }
    
    t = render_to_string('jswishlistdelete.html',context)
    return JsonResponse({'data': t})

# coupon
def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get('coupon_code', '').strip()
        user = request.user

        try:
            # Fetch cart and calculate total price
            cart = Cart.objects.get(user=user)
            cart_items = cart.items.filter(
                product__product_status="published",
                size_variant__size_status="published",
                size_variant__stock="stock_in"
            ).order_by('id')

            # if apply_coupon exists,delete that one
            discounted_price = request.session.get('discounted_price', None)
            if discounted_price is not None:  
                request.session.pop('discounted_price')
            original_prices = request.session.get('original_prices', None)
            if original_prices:
                for item in cart_items:
                    if str(item.id) in original_prices: 
                        item.price = Decimal(original_prices[str(item.id)])  
                        item.save()
                if 'original_prices' in request.session:
                    del request.session['original_prices']

            if not cart_items:
                return JsonResponse({
                    "success": False,
                    "message": "Your cart is empty. Add items to apply a coupon."
                })

            total_price = sum(item.total_price() for item in cart_items)

            # Check if the coupon exists and is valid
            coupon = Coupon.objects.get(code=coupon_code)
            if not coupon.is_valid():
                return JsonResponse({
                    "success": False,
                    "message": "Invalid or expired coupon."
                })
            
            if CouponUsage.objects.filter(user=user, coupon=coupon).exists():
                return JsonResponse({
                    "success": False,
                    "message": "You have already used this coupon."
                })

            cart_total = Decimal(total_price)

            # Validate minimum and maximum constraints
            if cart_total < coupon.min_purchase_amount:
                return JsonResponse({
                    "success": False,
                    "message": f"The total price must be at least ₹{coupon.min_purchase_amount} to apply this coupon."
                })

            if cart_total > coupon.max_discount_amount:
                return JsonResponse({
                    "success": False,
                    "message": f"The discount cannot exceed ₹{coupon.max_discount_amount}. Adjust your cart to use this coupon."
                })

            # Calculate discount
            discounted_price = coupon.apply_discount(cart_total)
            discount = cart_total-discounted_price
            request.session['discount']=float(discount)
            original_prices = {}
            for item in cart_items:
                original_prices[item.id] = str(Decimal(item.price))  # Convert Decimal to str

                # Apply the coupon discount to the item price
                price = Decimal(item.price)  # Convert to Decimal if it's not already
                new_price = coupon.apply_discount(price)

                # Update the item's price with the new discounted price
                item.price = new_price
                item.save()

            # Save original prices in session
            request.session['original_prices'] = original_prices
            
            request.session['discounted_price'] = float(discounted_price)
            request.session['coupon'] = coupon_code

            return JsonResponse({
                "success": True,
                "message": "Coupon applied successfully!",
                "discounted_price": float(discounted_price)
            })

        except Cart.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "No cart found for this user."
            })
        except Coupon.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Coupon not found."
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "An unexpected error occurred. Please try again."
            })

    return JsonResponse({
        "success": False,
        "message": "Invalid request."
    })
