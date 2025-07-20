from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
from django.utils.text import slugify
import random

# Category model for product categorization
class Category(models.Model):
    name = models.CharField(max_length=100)  # Category name
    slug = models.SlugField(max_length=100, unique=True, blank=True)  # Unique slug for URLs

    class Meta:
        verbose_name_plural = "Categories"  # Plural name in admin

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-generate unique slug if not set
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{random.randint(1000,9999)}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

# Subcategory model linked to Category
class Subcategory(models.Model):
    name = models.CharField(max_length=100)  # Subcategory name
    slug = models.SlugField(max_length=100, unique=True, blank=True)  # Unique slug for URLs
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')  # Parent category

    class Meta:
        verbose_name_plural = "Subcategories"  # Plural name in admin

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate unique slug if not set
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Subcategory.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{random.randint(1000,9999)}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

# Product model representing store items
class Product(models.Model):
    name = models.CharField(max_length=255)  # Product name
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # Unique slug for URLs
    description = models.TextField(blank=True)  # Product description
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Product image
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')  # Main category
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')  # Optional subcategory
    brand = models.CharField(max_length=100, blank=True, null=True)  # Brand name
    color = models.CharField(max_length=50, blank=True, null=True)  # Product color
    size = models.CharField(max_length=20, blank=True, null=True)  # Product size
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True, null=True)  # Last update timestamp

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-generate unique slug if not set
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{random.randint(1000,9999)}"
            self.slug = unique_slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        # Returns the URL for the product detail page
        return reverse('product_detail', args=[self.slug])
    
    def average_rating(self):
        # Calculates the average rating for the product
        from django.db.models import Avg
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

# Review model for product reviews
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')  # Reviewed product
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reviewer
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating value
    comment = models.TextField(blank=True)  # Optional comment
    created_at = models.DateTimeField(auto_now_add=True)  # Review timestamp

    class Meta:
        unique_together = ['product', 'user']  # One review per user per product

# Cart model for shopping carts
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique cart ID
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Associated user (optional)

# CartItem model for items in a cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # Parent cart
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Product in cart
    quantity = models.PositiveIntegerField(default=1)  # Quantity of product

    def total_price(self):
        # Returns total price for this cart item
        return self.product.price * self.quantity

# UserProfile model for additional user info
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Linked user
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)  # Profile image
    phone = models.CharField(max_length=20, blank=True, null=True)  # Phone number
    address = models.TextField(blank=True, null=True)  # Address
    wishlist = models.ManyToManyField(Product, blank=True)  # Wishlist products

    def __str__(self):
        return self.user.username

# RecentlyViewed model for tracking viewed products
class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who viewed
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Viewed product
    viewed_at = models.DateTimeField(auto_now_add=True)  # View timestamp