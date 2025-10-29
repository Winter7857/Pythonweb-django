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
    picture  = models.ImageField(upload_to="product_pics/",  null=True, blank=True)
    specfile = models.FileField(upload_to="product_specs/", null=True, blank=True)

    # Optional genre/group for filtering (e.g., FPS, MMORPG, Horror)
    GENRE_CHOICES = [
        ("fps", "FPS"),
        ("mmorpg", "MMORPG"),
        ("rpg", "RPG"),
        ("action", "Action"),
        ("adventure", "Adventure"),
        ("horror", "Horror"),
        ("sport", "Sport"),
        ("strategy", "Strategy"),
        ("sim", "Simulation"),
        ("other", "Other"),
    ]
    genre = models.CharField(max_length=32, choices=GENRE_CHOICES, null=True, blank=True)

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




