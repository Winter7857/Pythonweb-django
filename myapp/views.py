
from django.http import HttpResponse
from django.shortcuts import *
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from .models import Contact, Action



# Create your views here.
def home1(request):
    return HttpResponse("Hello, world! This is my Django app.")
def home2(request):
    return HttpResponse("Hello world2")
# def home(request): 
#     return render(request, 'myapp/home.html')  # Render a template named 'home.html'
def aboutUs(request):
    return render(request, 'myapp/aboutus.html')  # Render a template named 'about.html'
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product

def home(request):
    product_list = Product.objects.all().order_by('-id')
    paginator = Paginator(product_list, 4)  # 4 products per page

    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'myapp/home.html', {
        'pd': page_obj.object_list,
        'page_obj': page_obj,
    })

    
def aboutUS(request):
        return render(request, 'myapp/aboutus.html')


def contactus(request):
    context = {}  # default

    if request.method == "POST":
        topic  = request.POST.get("topic")
        email  = request.POST.get("email")
        detail = request.POST.get("detail")
        if(topic=="" or email=="" or detail==""):
            context = {
            'message': '❌ Please fill all the fields',
            'topic': topic,
            'email': email,
            'detail': detail,
        }
        # save to database
        Contact.objects.create(
            topic=topic,
            email=email,
            detail=detail
        )

        print(topic, email, detail)

        context = {
            'message': '✅ Your message has been saved to the database!',
            'topic': topic,
            'email': email,
            'detail': detail,
        }
    return render(request, "myapp/contact.html", context)

# def userLogin(request):
#     message = None
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect("home")  # go to homepage after login
#         else:
#             message = "❌ Invalid username or password."

#     return render(request, "myapp/login.html", {"message": message})
def userLogin(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # go to home page after login
                return redirect("home-page")
            else:
                context["message"] = "❌ Username or password is incorrect."
        except Exception:
            context["message"] = "❌ Login failed. Try again."

    return render(request, "myapp/login.html", context)

def userLogout(request):
    logout(request)
    return redirect('login')
# Helper: allow only staff/admin users
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def showContact(request):
    allcontact = Contact.objects.all().order_by('-id')  # newest first
    context = {'contact': allcontact}
    return render(request, 'myapp/showcontact.html', context)

def userRegist(request):
    message = None
    if request.method == "POST":
        username   = request.POST.get("username")
        password   = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name  = request.POST.get("last_name")
        email      = request.POST.get("email")

        if User.objects.filter(username=username).exists():
            message = "❌ Username already exists."
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            # also create Profile automatically
            from .models import Profile
            Profile.objects.create(user=user)

            return redirect("login")  # after register, go to login

    return render(request, "myapp/register.html", {"message": message})
def userProfile(request):
    # make sure a profile exists for this user
    profile, _ = Profile.objects.get_or_create(user=request.user)
    context = {"profile": profile}
    return render(request, "myapp/profile.html", context)

@login_required
def editProfile(request):
    # ensure the user has a profile
    profile, _ = Profile.objects.get_or_create(user=request.user)
    context = {"profile": profile}

    if request.method == "POST":
        data = request.POST.copy()
        first_name = data.get("first_name", "").strip()
        last_name  = data.get("last_name", "").strip()
        username   = data.get("username", "").strip()
        email      = data.get("email", "").strip()
        password   = data.get("password", "")  # keep if blank

        # basic validation
        if not (first_name and last_name and username and email):
            context["message"] = "❌ Please fill all required fields."
            return render(request, "myapp/editprofile.html", context)

        # avoid duplicate usernames (allow keeping current)
        if username != request.user.username and User.objects.filter(username=username).exists():
            context["message"] = "❌ Username already taken."
            return render(request, "myapp/editprofile.html", context)

        # update user
        user = request.user
        user.first_name = first_name
        user.last_name  = last_name
        user.username   = username
        user.email      = email
        if password:
            user.set_password(password)
        user.save()

        # re-authenticate if we changed password/username
        try:
            user = authenticate(request, username=username, password=password or None)
            # If password not changed, authenticate returns None; just keep session
            if user:
                login(request, user)
        except Exception:
            pass

        context["message"] = "✅ Profile updated successfully."
        # refresh profile in context
        context["profile"] = Profile.objects.get(user=request.user)

    return render(request, "myapp/editprofile.html", context)
def addproduct(request):
    # Render empty form on GET
    if request.method != 'POST':
        return render(request, 'myapp/addproduct.html')

    if request.method == 'POST':
        data = request.POST.copy()
        title = data.get('title')
        description = data.get('description')
        price = data.get('price')
        quantity = data.get('quantity')
        instock = data.get('instock')

        # Create product instance (without saving yet)
        new = Product(
            title=title,
            description=description,
            price=price,
            quantity=quantity,
            instock=bool(instock)
        )

        # === IMAGE UPLOAD ===
        if 'picture' in request.FILES:
            file_image = request.FILES['picture']
            file_image_name = file_image.name.replace(' ', '_')
            fs = FileSystemStorage(location='media/product/')
            filename = fs.save(file_image_name, file_image)
            upload_file_url = fs.url(filename)
            print("Picture URL:", upload_file_url)
            new.picture = 'product/' + upload_file_url[6:]

        # === SPEC FILE UPLOAD ===
        if 'specfile' in request.FILES:
            file_specfile = request.FILES['specfile']
            file_specfile_name = file_specfile.name.replace(' ', '_')
            fs = FileSystemStorage(location='media/specfile/')
            filename = fs.save(file_specfile_name, file_specfile)
            upload_file_url = fs.url(filename)
            print("Spec File URL:", upload_file_url)
            new.specfile = 'specfile/' + upload_file_url[6:]

        # Save product to DB
        new.save()
        return render(request, 'myapp/addproduct.html', {'message': '✅ Product added successfully!'})

@login_required
@user_passes_test(is_admin)
def editproduct_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'myapp/editproduct_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def editproduct(request, pid):
    product = get_object_or_404(Product, id=pid)
    message = None

    if request.method == 'POST':
        data = request.POST.copy()
        product.title = data.get('title', product.title)
        product.description = data.get('description', product.description)
        product.price = data.get('price') or product.price
        product.quantity = data.get('quantity') or product.quantity
        product.instock = bool(data.get('instock'))

        # Optional file replacements
        if 'picture' in request.FILES:
            file_image = request.FILES['picture']
            try:
                product.picture.save(file_image.name.replace(' ', '_'), file_image, save=False)
            except Exception:
                pass

        if 'specfile' in request.FILES:
            file_spec = request.FILES['specfile']
            try:
                product.specfile.save(file_spec.name.replace(' ', '_'), file_spec, save=False)
            except Exception:
                pass

        product.save()
        message = '✅ Product updated successfully.'

    return render(request, 'myapp/editproduct_form.html', {'p': product, 'message': message})

@login_required
@user_passes_test(is_admin)
def deleteproduct_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'myapp/deleteproduct_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def deleteproduct(request, pid):
    product = get_object_or_404(Product, id=pid)
    if request.method == 'POST':
        product.delete()
        return redirect('deleteproduct-list')
    return render(request, 'myapp/deleteproduct_confirm.html', {'p': product})

@login_required
def cart_page(request):
    # Placeholder cart page for authenticated users
    return render(request, 'myapp/cart.html', {})


def handler404(request, exception=None):
    return render(request, 'myapp/404errorPage.html', status=404)


def actionPage(request, cid):
    contact = get_object_or_404(Contact, pk=cid)
    actions = Action.objects.filter(contact=contact).order_by('-id')

    if request.method == 'POST':
        data = request.POST
        actiondetail = (data.get('actiondetail') or '').strip()

        if 'save' in data:
            if actiondetail:
                Action.objects.create(contact=contact, actionDetail=actiondetail)
            return redirect('action-page', cid=contact.id)

        elif 'delete_action' in data:
            action_id = data.get('action_id')
            Action.objects.filter(id=action_id, contact=contact).delete()
            return redirect('action-page', cid=contact.id)

        elif 'delete_contact' in data:
            contact.delete()
            return redirect('showcontact-page')

        elif 'complete' in data:
            contact.complete = True
            contact.save()
            return redirect('showcontact-page')

    context = {
        'contact': contact,
        'actions': actions,
        'last_action': actions.first() if actions.exists() else None,
    }
    return render(request, 'myapp/action.html', context)
    contact = get_object_or_404(Contact, pk=cid)
    context = {'contact': contact}

    # history (newest first)
    actions = Action.objects.filter(contact=contact).order_by('-id')
    context['actions'] = actions
    context['last_action'] = actions.first() if actions.exists() else None

    if request.method == 'POST':
        data = request.POST
        actiondetail = (data.get('actiondetail') or '').strip()

        if 'save' in data:
            if actiondetail:
                Action.objects.create(contact=contact, actionDetail=actiondetail)
            return redirect('action-page', cid=contact.id)

        elif 'delete' in data:
            contact.delete()
            return redirect('showcontact-page')

        elif 'complete' in data:
            contact.complete = True
            contact.save()
            return redirect('showcontact-page')

    return render(request, 'myapp/action.html', context)




