from django.contrib import admin
from .models import *
from django.contrib import admin
from .models import Product, Contact, Profile

# Register your models here.

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Profile)
admin.site.register(Action)
