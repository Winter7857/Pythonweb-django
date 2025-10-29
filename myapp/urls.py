# from django.urls import path
# from .views import *
# from django.contrib.auth import views
# from myapp.views import userLogin   # <-- add this


# #http://127.0.0.1:8000/admin/
# urlpatterns =[
#     path('home/', home1, name='home'),  # Define the home view
#     path('home2/', home2, name='home2'),  # Define the home2 view
#     path('', home, name='home-page'),  # Define the home view that renders a template
#     path('about/', aboutUs, name='about-page'),  # Define the aboutus view that renders a template
#     path('contact/', contactus, name='contact-page'),  # Define the contactus view that renders a template
#     path('login/', userLogin, name="login"),
#     path('logout/', userLogout, name="logout"),
#     path('showcontact/', showContact, name='showcontact-page'),
#     path('register/', userRegist, name='register'),
#     path("profile/", userProfile, name="profile-page"),
#     path('editprofile/', editProfile,  name='editprofile-page'),
#     path('addproduct/', addProduct, name='addproduct-page'),

    
# ]

from django.urls import path
from .views import *
from django.contrib.auth import views
from myapp.views import userLogin   # custom login view
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
# http://127.0.0.1:8000/admin/
urlpatterns = [
    path('home/', home1, name='home'),
    path('home2/', home2, name='home2'),
    path('', home, name='home-page'),
    path('about/', aboutUs, name='about-page'),
    path('contact/', contactus, name='contact-page'),
    
    # --- Auth routes ---
    path('login/', userLogin, name='login'),
    path('logout/', userLogout, name='logout'),
    path('register/', userRegist, name='register'),

    # --- Profile routes ---
    path("profile/", userProfile, name="profile-page"),
    path('editprofile/', editProfile, name='editprofile-page'),

    # --- Contact list (admin only) ---
    path('showcontact/', showContact, name='showcontact-page'),
    
    # --- Product upload/download ---
    path('addproduct/', addproduct, name='addproduct-page'),
    path('action/<int:cid>/', actionPage, name='action-page'),  
    # --- Product management (admin) ---
    path('products/', editproduct_list, name='editproduct-list'),
    path('products/<int:pid>/edit/', editproduct, name='editproduct'),
    # --- Product delete (admin) ---
    path('products/delete/', deleteproduct_list, name='deleteproduct-list'),
    path('products/<int:pid>/delete/', deleteproduct, name='deleteproduct'),
    # --- Cart (user) ---
    path('cart/', cart_page, name='cart-page'),
    # Cart API (session based)
    path('api/cart/', cart_api_items, name='cart-api-items'),
    path('api/cart/add/', cart_api_add, name='cart-api-add'),
    path('api/cart/remove/', cart_api_remove, name='cart-api-remove'),
    path('api/cart/clear/', cart_api_clear, name='cart-api-clear'),
    path('api/cart/checkout/', cart_api_checkout, name='cart-api-checkout'),

    # --- Admin: User roles --- (avoid clashing with Django admin at /admin/)
    path('manage/users/', user_roles, name='user-roles'),
    
]
if settings.DEBUG:
    # Media (user uploads)  -> uses django.conf.urls.static.static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Static (your CSS/JS from STATICFILES_DIRS / app 'static' folders)
    urlpatterns += staticfiles_urlpatterns()
