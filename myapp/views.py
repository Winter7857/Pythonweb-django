
from django.http import HttpResponse
from django.http import JsonResponse
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
from django.core.files.base import ContentFile
from .models import Contact, Action
from django.db import transaction
from django.db.models import F, Q
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from decimal import Decimal
from .models import Order, OrderItem, ProductRating
from django.db.models import Avg, Count



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
    # Base queryset with rating annotations
    base_qs = (
        Product.objects
        .all()
        .annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings')
        )
    )

    # Read filters
    q = (request.GET.get('q') or '').strip()
    min_rating_raw = (request.GET.get('min_rating') or '').strip()
    price_min_raw = (request.GET.get('price_min') or '').strip()
    price_max_raw = (request.GET.get('price_max') or '').strip()
    sort = (request.GET.get('sort') or 'newest').strip()

    # Apply search
    if q:
        base_qs = base_qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # Apply price range (on queryset)
    price_min = None
    price_max = None
    try:
        if price_min_raw != '':
            price_min = Decimal(price_min_raw)
            if price_min < 0:
                price_min = Decimal('0')
    except (ArithmeticError, ValueError):
        price_min = None
    try:
        if price_max_raw != '':
            price_max = Decimal(price_max_raw)
            if price_max < 0:
                price_max = None
    except (ArithmeticError, ValueError):
        price_max = None
    # Normalize if min > max
    if price_min is not None and price_max is not None and price_min > price_max:
        price_min, price_max = price_max, price_min

    if price_min is not None:
        base_qs = base_qs.filter(price__gte=price_min)
    if price_max is not None:
        base_qs = base_qs.filter(price__lte=price_max)

    # Materialize list for rating filtering and sorting only
    all_products = list(base_qs)

    # Apply min rating (on the in-memory list)
    try:
        min_rating = int(min_rating_raw) if min_rating_raw else 0
    except (TypeError, ValueError):
        min_rating = 0
    if min_rating:
        all_products = [p for p in all_products if (getattr(p, 'avg_rating', 0) or 0) >= min_rating]


    # Sorting
    # Sorting (works on list)
    if sort == 'price_asc':
        product_list = sorted(all_products, key=lambda p: (p.price is None, p.price, -p.id))
    elif sort == 'price_desc':
        product_list = sorted(all_products, key=lambda p: (p.price is None, -(p.price or 0), -p.id))
    elif sort == 'rating_desc':
        product_list = sorted(all_products, key=lambda p: (-(getattr(p, 'avg_rating', 0) or 0), -(getattr(p, 'rating_count', 0) or 0), -p.id))
    elif sort == 'title_asc':
        product_list = sorted(all_products, key=lambda p: (p.title or '').lower())
    elif sort == 'title_desc':
        product_list = sorted(all_products, key=lambda p: (p.title or '').lower(), reverse=True)
    else:  # newest
        product_list = sorted(all_products, key=lambda p: -p.id)

    # Pagination
    paginator = Paginator(product_list, 4)
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
        'q': q,
        'min_rating': min_rating,
        'sort': sort,
        'price_min': (str(price_min) if price_min is not None else ''),
        'price_max': (str(price_max) if price_max is not None else ''),
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

    # User's purchased products (unique by product)
    items = (
        OrderItem.objects
        .filter(order__user=request.user)
        .select_related('product', 'order')
        .order_by('-order__created_at')
    )
    # dedupe by product keeping latest appearance
    seen = set()
    purchased_products = []
    for it in items:
        if it.product_id and it.product_id not in seen and it.product is not None:
            seen.add(it.product_id)
            purchased_products.append(it.product)

    # User's ratings map
    ratings = ProductRating.objects.filter(user=request.user, product__in=purchased_products)
    ratings_by_pid = {r.product_id: r for r in ratings}
    for p in purchased_products:
        r = ratings_by_pid.get(p.id)
        setattr(p, 'user_rating', r.rating if r else 0)

    context = {
        "profile": profile,
        "purchased_products": purchased_products,
        "ratings_by_pid": ratings_by_pid,
    }
    return render(request, "myapp/profile.html", context)

@login_required
@csrf_protect
def rate_product(request):
    if request.method != 'POST':
        return JsonResponse({"ok": False, "error": "POST required"}, status=405)
    try:
        product_id = int(request.POST.get('product_id') or '0')
        stars = int(request.POST.get('rating') or '0')
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid input"}, status=400)

    stars = max(1, min(5, stars))
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return JsonResponse({"ok": False, "error": "Product not found"}, status=404)

    # Optional gate: must have purchased
    has_bought = OrderItem.objects.filter(order__user=request.user, product_id=product_id).exists()
    if not has_bought:
        return JsonResponse({"ok": False, "error": "Only buyers can rate"}, status=403)

    rating_obj, _ = ProductRating.objects.get_or_create(user=request.user, product=product)
    rating_obj.rating = stars
    comment = (request.POST.get('comment') or '').strip()
    if comment:
        rating_obj.comment = comment
    rating_obj.save()

    agg = ProductRating.objects.filter(product=product).aggregate(avg=Avg('rating'), count=Count('id'))
    return JsonResponse({
        "ok": True,
        "rating": rating_obj.rating,
        "average": round(float(agg['avg'] or 0), 2),
        "count": int(agg['count'] or 0),
    })

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
        # Sanitize numeric inputs: default to 0 if empty
        from decimal import Decimal, InvalidOperation
        price_raw = (data.get('price') or '').strip()
        try:
            price_val = Decimal(price_raw) if price_raw != '' else Decimal('0')
        except InvalidOperation:
            price_val = Decimal('0')
        qty_raw = (data.get('quantity') or '').strip()
        try:
            quantity_val = int(qty_raw) if qty_raw != '' else 0
        except (TypeError, ValueError):
            quantity_val = 0
        # Create product instance (without stock management)
        new = Product(
            title=title,
            description=description,
            price=price_val,
        )

        # === IMAGE UPLOAD or URL ===
        image_url = (data.get('image_url') or '').strip()
        if 'picture' in request.FILES and request.FILES['picture']:
            file_image = request.FILES['picture']
            file_image_name = file_image.name.replace(' ', '_')
            fs = FileSystemStorage(location='media/product/')
            filename = fs.save(file_image_name, file_image)
            upload_file_url = fs.url(filename)
            print("Picture URL:", upload_file_url)
            new.picture = 'product/' + upload_file_url[6:]
        elif image_url:
            try:
                import urllib.request, os
                resp = urllib.request.urlopen(image_url, timeout=10)
                data_bytes = resp.read()
                content_type = resp.headers.get('Content-Type', '')
                ext = 'jpg'
                if 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'jpeg' in content_type:
                    ext = 'jpg'
                base = os.path.basename(urllib.request.urlparse(image_url).path) or f'image.{ext}'
                if '.' not in base:
                    base = f'{base}.{ext}'
                safe_name = base.replace(' ', '_')
                new.picture.save(safe_name, ContentFile(data_bytes), save=False)
            except Exception as e:
                print('Image URL download failed:', e)

        # === TRAILER URL ===
        trailer_url = (data.get('trailer_url') or '').strip()
        if trailer_url:
            new.trailer_url = trailer_url

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
        # Trailer URL
        product.trailer_url = (data.get('trailer_url') or product.trailer_url)

        # Optional file replacements
        image_url = (data.get('image_url') or '').strip()
        if 'picture' in request.FILES and request.FILES['picture']:
            file_image = request.FILES['picture']
            try:
                product.picture.save(file_image.name.replace(' ', '_'), file_image, save=False)
            except Exception:
                pass
        elif image_url:
            try:
                import urllib.request, urllib.parse, os
                resp = urllib.request.urlopen(image_url, timeout=10)
                data_bytes = resp.read()
                content_type = resp.headers.get('Content-Type', '')
                ext = 'jpg'
                if 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'jpeg' in content_type:
                    ext = 'jpg'
                path = urllib.parse.urlparse(image_url).path
                base = os.path.basename(path) or f'image.{ext}'
                if '.' not in base:
                    base = f'{base}.{ext}'
                safe_name = base.replace(' ', '_')
                product.picture.save(safe_name, ContentFile(data_bytes), save=False)
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
    # Cart page with discount context by user role
    discount_percent = 0
    role = ''
    try:
        if request.user.is_authenticated:
            role = (getattr(request.user.profile, 'usertype', '') or '').lower()
            mapping = {'member': 5, 'vip': 10, 'vvip': 15}
            discount_percent = mapping.get(role, 0)
    except Exception:
        pass

    return render(request, 'myapp/cart.html', {
        'discount_percent': discount_percent,
        'user_role': role,
    })

# ---- Admin: Orders report ----
@login_required
@user_passes_test(is_admin)
def orders_report(request):
    qs = Order.objects.all().select_related('user').order_by('-created_at')

    # Optional filters
    start = request.GET.get('start')
    end = request.GET.get('end')
    user_q = request.GET.get('user')
    if start:
        from django.utils.dateparse import parse_datetime, parse_date
        from django.utils.timezone import make_aware
        from datetime import datetime, time
        d = parse_date(start)
        if d:
            qs = qs.filter(created_at__gte=make_aware(datetime.combine(d, time.min)))
    if end:
        from django.utils.dateparse import parse_date
        from django.utils.timezone import make_aware
        from datetime import datetime, time
        d = parse_date(end)
        if d:
            qs = qs.filter(created_at__lte=make_aware(datetime.combine(d, time.max)))
    if user_q:
        qs = qs.filter(user__username__icontains=user_q)

    # CSV export
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="orders.csv"'
        writer = csv.writer(resp)
        writer.writerow(['Order ID', 'User', 'Date', 'Subtotal', 'Discount %', 'Total', 'Items'])
        for o in qs:
            items_str = "; ".join([f"{it.name} x{it.quantity} ({it.price})" for it in o.items.all()])
            writer.writerow([o.id, getattr(o.user, 'username', ''), o.created_at.strftime('%Y-%m-%d %H:%M'), f"{o.subtotal:.2f}", o.discount_percent, f"{o.total:.2f}", items_str])
        return resp

    # Aggregates
    total_orders = qs.count()
    total_revenue = qs.aggregate(s=models.Sum('total'))['s'] or Decimal('0.00')
    return render(request, 'myapp/orders_report.html', {
        'orders': qs[:200],  # safety cap
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'start': start or '',
        'end': end or '',
        'user_q': user_q or '',
    })

# ---- Cart API (session-based) ----
from django.views.decorators.http import require_http_methods

SESSION_CART_KEY = 'cart_product_ids'

def _get_session_cart_ids(request):
    ids = request.session.get(SESSION_CART_KEY) or []
    # ensure string list
    return [str(x) for x in ids]

def _set_session_cart_ids(request, ids):
    request.session[SESSION_CART_KEY] = [str(x) for x in (ids or [])]
    request.session.modified = True

@login_required
@require_http_methods(["GET"])
def cart_api_items(request):
    ids = _get_session_cart_ids(request)
    if not ids:
        return JsonResponse({"items": []})
    qs = Product.objects.filter(id__in=ids)
    items = []
    for p in qs:
        items.append({
            "id": str(p.id),
            "name": p.title,
            "price": float(p.price or 0),
            "image": p.picture.url if getattr(p, 'picture', None) and p.picture else "",
        })
    # keep original order roughly by ids list
    items.sort(key=lambda x: ids.index(str(x["id"])) if str(x["id"]) in ids else 0)
    return JsonResponse({"items": items})

@login_required
@require_http_methods(["POST"])
def cart_api_add(request):
    pid = (request.POST.get('product_id') or '').strip()
    if not pid:
        return JsonResponse({"error": "product_id required"}, status=400)
    # validate product exists
    if not Product.objects.filter(id=pid).exists():
        return JsonResponse({"error": "product not found"}, status=404)
    ids = _get_session_cart_ids(request)
    if pid not in ids:
        ids.append(pid)
        _set_session_cart_ids(request, ids)
    return JsonResponse({"ok": True, "count": len(ids)})

@login_required
@require_http_methods(["POST", "DELETE"])
def cart_api_remove(request):
    pid = (request.POST.get('product_id') or '').strip()
    if not pid:
        return JsonResponse({"error": "product_id required"}, status=400)
    ids = _get_session_cart_ids(request)
    if pid in ids:
        ids = [x for x in ids if x != pid]
        _set_session_cart_ids(request, ids)
    return JsonResponse({"ok": True, "count": len(ids)})

@login_required
@require_http_methods(["POST"])
def cart_api_clear(request):
    _set_session_cart_ids(request, [])
    return JsonResponse({"ok": True, "count": 0})

@login_required
@require_http_methods(["POST"])
def cart_api_checkout(request):
    ids = _get_session_cart_ids(request)
    if not ids:
        return JsonResponse({"error": "empty_cart"}, status=400)

    processed = []
    out_of_stock = []  # preserved for API shape, but unused now
    items_snapshot = []  # (product, name, price)

    with transaction.atomic():
        qs = Product.objects.filter(id__in=ids)
        for p in qs:
            processed.append(str(p.id))
            items_snapshot.append((p, p.title, Decimal(p.price or 0)))
        # Clear cart after attempt
        _set_session_cart_ids(request, [])

    # Create order for processed items
    order_id = None
    if processed:
        try:
            # Determine discount by role (same mapping as cart_page)
            discount_percent = 0
            try:
                role = (getattr(request.user.profile, 'usertype', '') or '').lower()
                discount_percent = {'member': 5, 'vip': 10, 'vvip': 15}.get(role, 0)
            except Exception:
                pass

            subtotal = sum((price for (_p, _n, price) in items_snapshot), Decimal('0.00'))
            total = subtotal * (Decimal('1.00') - Decimal(discount_percent) / Decimal('100'))
            order = Order.objects.create(
                user=request.user,
                subtotal=subtotal,
                discount_percent=discount_percent,
                total=total,
            )
            order_id = order.id
            for (prod, name, price) in items_snapshot:
                OrderItem.objects.create(order=order, product=prod, name=name, price=price, quantity=1)
        except Exception:
            # Do not fail checkout if reporting fails; still return processed ids
            order_id = None

    return JsonResponse({
        "ok": True,
        "processed": processed,
        "out_of_stock": out_of_stock,
        "order_id": order_id,
    })


# -------- Admin: Manage user roles --------
@login_required
@user_passes_test(is_admin)
@csrf_protect
def user_roles(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = (request.POST.get('usertype') or '').strip().lower()
        allowed = {'member', 'vip', 'vvip'}
        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect('user-roles')

        if new_role not in allowed:
            messages.error(request, 'Invalid role selected.')
            return redirect('user-roles')

        # Ensure profile exists
        prof, _ = Profile.objects.get_or_create(user=target)
        prof.usertype = new_role
        prof.save(update_fields=['usertype'])
        messages.success(request, f"Updated {target.username}'s role to {new_role.upper()}.")
        return redirect('user-roles')

    # GET: list users with profiles
    users = User.objects.all().select_related('profile').order_by('username')
    return render(request, 'myapp/user_roles.html', { 'users': users })


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




