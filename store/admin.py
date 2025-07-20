from django.contrib import admin
from .models import Category, Subcategory, Product, Review, Cart, CartItem, UserProfile, RecentlyViewed

# Admin configuration for Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')  # Fields to display in admin list view
    prepopulated_fields = {'slug': ('name',)}  # Auto-populate slug from name

# Admin configuration for Subcategory model
@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category')  # Fields to display
    prepopulated_fields = {'slug': ('name',)}  # Auto-populate slug
    list_filter = ('category',)  # Filter by category in admin

# Admin configuration for Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'subcategory', 'price', 'brand', 'color', 'size')  # Fields to display
    search_fields = ('name', 'description')  # Enable search by name and description
    list_filter = ('category', 'subcategory', 'brand', 'color', 'size')  # Filters in admin
    prepopulated_fields = {'slug': ('name',)}  # Auto-populate slug

# Admin configuration for Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')  # Fields to display
    list_filter = ('rating', 'created_at')  # Filters in admin

# Admin configuration for Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')  # Fields to display
    list_filter = ('created_at',)  # Filter by creation date

# Admin configuration for CartItem model
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')  # Fields to display

# Admin configuration for UserProfile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')  # Fields to display

# Admin configuration for RecentlyViewed model
@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'viewed_at')  # Fields to display
    list_filter = ('user',)  # Filter by user