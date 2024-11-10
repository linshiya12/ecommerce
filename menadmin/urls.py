from django.urls import path
from . import views

urlpatterns = [
    path('adminproductlist/',views.productlist,name="productlist"),
    path('adproductedit/',views.productedit,name="productedit"),
    path('adproductadd/',views.productadd,name="productadd"),
]

