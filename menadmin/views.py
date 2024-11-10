from django.shortcuts import render
from django.http import HttpResponse
from user.models import *


# Create your views here.
def productlist(request):
    products=Product.objects.all()
    
    context={
        "products":products,

    }
    
    return render(request,"adminproductlist.html",context)

def productedit(request):
    # products=Product.objects.get(id=id)
    # context={
    #     "products":products,

    # }
    return render(request,"adproductedit.html")

def productadd(request):
    
    return render(request,"adproductadd.html")






# Create your views here.
