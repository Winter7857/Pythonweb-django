from django.db import models
from django.http import HttpResponse
from django.shortcuts import *
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, \
                                null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    instock = models.BooleanField(default=True)
    def __str__(self):   
        return self.title
    # def home(request): 
    #     allproducts = Product.objects.all()
    #     context = {'pd': allproducts}
    #     return render(request, 'myapp/home.html', context)  # Render a template named
    # def aboutUS(request):
    #     return render(request, 'myapp/aboutus.html')

class Contact(models.Model):
    topic = models.CharField(max_length=200)
    email = models.EmailField()
    detail = models.TextField()
    complete = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.topic
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usertype = models.CharField(max_length=100, default='member')   # member / vip / vvip
    point = models.IntegerField(default=0)


    def __str__(self):
        return self.user.username
    
    from django.db import models

class Product(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity    = models.IntegerField(null=True, blank=True)
    instock     = models.BooleanField(default=True)

    # NEW (upload targets: /media/product_pics/ and /media/product_specs/)
    picture     = models.ImageField(upload_to="product_pics/",  null=True, blank=True)
    specfile    = models.FileField(upload_to="product_specs/", null=True, blank=True)  # legacy, no longer used
    trailer_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
    
class Action(models.Model):
    # if you ALREADY have an old column called contactList_id in the DB,
    # keep it with db_column to avoid data migration:
    # contact = models.ForeignKey(Contact, on_delete=models.CASCADE, db_column='contactList_id')

    # Otherwise (fresh/clean), just use the default:
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    actionDetail = models.TextField()

    def __str__(self):
        return self.contact.topic


# ---- Orders for checkout reporting ----
from decimal import Decimal

class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_percent = models.IntegerField(default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        uname = self.user.username if self.user else 'anon'
        return f"Order #{self.id} by {uname} ({self.created_at:%Y-%m-%d})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity = models.IntegerField(default=1)

    def line_total(self):
        return (self.price or Decimal('0.00')) * self.quantity

    def __str__(self):
        return f"{self.name} x{self.quantity}"




