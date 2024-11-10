from django.urls import path
from . import views

urlpatterns = [
    path('',views.create,name="home"),
    path('contact/',views.contact,name="contact"),
    path('blog/',views.blog,name="blog"),
    path('cart/',views.cart,name="cart"),
    path('wishlist/',views.wishlist,name="wishlist"),
    path('shop/',views.shop,name="shop"),
    path('product/<int:id>',views.product,name="product_detail"),
    path('get-variant-images/<id>/',views.get_variant_images,name="get_variant_images")
]