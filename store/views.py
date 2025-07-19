from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Sum
from django.http import JsonResponse
from .models import Category, Subcategory, Product, Review, Cart, CartItem, UserProfile, RecentlyViewed
from .forms import UserRegistrationForm, LoginForm, UserUpdateForm, ProfileUpdateForm, ReviewForm
import random
from django.conf import settings  # Import settings to access DEBUG

def get_cart(request):
    """Get or create cart for the current session"""
    if request.user.is_authenticated:
        # For authenticated users, get or create user-specific cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    
    # For anonymous users, use session-based cart
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            pass
    
    # Create new cart
    cart = Cart.objects.create()
    request.session['cart_id'] = str(cart.id)
    return cart

def cart_count(request):
    """View to get cart count for AJAX requests"""
    try:
        cart = get_cart(request)
        count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({'count': count})
    except Exception:
        return JsonResponse({'count': 0})

def home(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    brand = request.GET.get('brand')
    color = request.GET.get('color')
    size = request.GET.get('size')

    products = Product.objects.all().prefetch_related('reviews')
    
    # Initialize filter lists
    categories = Category.objects.all()
    brands = []
    colors = []
    sizes = []
    
    try:
        brands = Product.objects.exclude(brand__isnull=True).exclude(brand__exact='').values_list('brand', flat=True).distinct()
        colors = Product.objects.exclude(color__isnull=True).exclude(color__exact='').values_list('color', flat=True).distinct()
        sizes = Product.objects.exclude(size__isnull=True).exclude(size__exact='').values_list('size', flat=True).distinct()
    except Exception as e:
        # Use settings.DEBUG instead of DEBUG
        if settings.DEBUG:
            messages.warning(request, f"Database error: {str(e)}")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category_id:
        products = products.filter(category_id=category_id)

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if brand:
        products = products.filter(brand=brand)

    if color:
        products = products.filter(color=color)

    if size:
        products = products.filter(size=size)

    # For recently viewed
    recently_viewed = None
    if request.user.is_authenticated:
        recently_viewed = RecentlyViewed.objects.filter(user=request.user).order_by('-viewed_at')[:5]

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'colors': colors,
        'sizes': sizes,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'selected_brand': brand,
        'selected_color': color,
        'selected_size': size,
        'recently_viewed': recently_viewed,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, slug):
    try:
        product = get_object_or_404(Product, slug=slug)
    except Product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect('home')
    
    # Add to recently viewed
    if request.user.is_authenticated:
        # Check if already viewed recently
        if not RecentlyViewed.objects.filter(user=request.user, product=product).exists():
            RecentlyViewed.objects.create(user=request.user, product=product)
    
    # Get reviews
    reviews = product.reviews.all().order_by('-created_at')
    average_rating = product.average_rating()
    
    # Check if user has reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, product=product).first()
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_review': user_review,
    }
    return render(request, 'store/product_detail.html', context)

def category_view(request, slug):
    try:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category)
        return render(request, 'store/home.html', {
            'products': products,
            'category': category,
        })
    except Category.DoesNotExist:
        messages.error(request, "Category not found")
        return redirect('home')

def subcategory_view(request, slug):
    try:
        subcategory = get_object_or_404(Subcategory, slug=slug)
        products = Product.objects.filter(subcategory=subcategory)
        return render(request, 'store/home.html', {
            'products': products,
            'subcategory': subcategory,
        })
    except Subcategory.DoesNotExist:
        messages.error(request, "Subcategory not found")
        return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile(request):
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)
    
    return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def dashboard(request):
    # Recently viewed
    recently_viewed = RecentlyViewed.objects.filter(user=request.user).order_by('-viewed_at')[:10]
    
    # Wishlist
    wishlist = request.user.userprofile.wishlist.all()
    
    # Reviews
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Cart items
    cart = get_cart(request)
    
    context = {
        'recently_viewed': recently_viewed,
        'wishlist': wishlist,
        'reviews': reviews,
        'cart': cart,
    }
    return render(request, 'store/dashboard.html', context)

@login_required
def cart_view(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    total = sum(item.total_price() for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        cart = get_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
        messages.info(request, 'Item removed from cart')
    except CartItem.DoesNotExist:
        messages.error(request, 'Item not found in cart')
    
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.info(request, 'Cart updated')
        else:
            cart_item.delete()
            messages.info(request, 'Item removed from cart')
    except (CartItem.DoesNotExist, ValueError):
        messages.error(request, 'Invalid request')
    
    return redirect('cart')

@login_required
def add_review(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review, created = Review.objects.update_or_create(
                    user=request.user,
                    product=product,
                    defaults={
                        'rating': form.cleaned_data['rating'],
                        'comment': form.cleaned_data['comment']
                    }
                )
                messages.success(request, 'Review submitted!')
                return redirect('product_detail', slug=product.slug)
        else:
            form = ReviewForm()
        
        return render(request, 'store/product_detail.html', {
            'product': product,
            'review_form': form
        })
        
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('home')

@login_required
def add_to_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        profile = request.user.userprofile
        
        if product not in profile.wishlist.all():
            profile.wishlist.add(product)
            messages.success(request, f'{product.name} added to wishlist')
        else:
            messages.info(request, f'{product.name} is already in your wishlist')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        profile = request.user.userprofile
        
        if product in profile.wishlist.all():
            profile.wishlist.remove(product)
            messages.info(request, f'{product.name} removed from wishlist')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def checkout(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    total = sum(item.total_price() for item in cart_items)
    
    if request.method == 'POST':
        # Simulate purchase
        cart.items.all().delete()
        messages.success(request, 'Purchase completed successfully!')
        return redirect('dashboard')
    
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })