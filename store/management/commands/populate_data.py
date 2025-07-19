from django.core.management.base import BaseCommand
from store.models import Category, Subcategory, Product, UserProfile
import decimal
from django.contrib.auth.models import User
from django.core.files import File
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from io import BytesIO
import time
import ssl

class Command(BaseCommand):
    help = 'Populates the database with sample data'
    
    def handle(self, *args, **kwargs):
        # Clear existing data
        Product.objects.all().delete()
        Subcategory.objects.all().delete()
        Category.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(username__in=['testuser', 'admin']).delete()
        
        # Create test user
        user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=user)
        
        # Create categories
        shirts = Category.objects.create(name="Shirts")
        pants = Category.objects.create(name="Pants")
        accessories = Category.objects.create(name="Accessories")
        shoes = Category.objects.create(name="Shoes")
        
        # Create subcategories
        mens_shirts = Subcategory.objects.create(name="Men's", category=shirts)
        womens_shirts = Subcategory.objects.create(name="Women's", category=shirts)
        jeans = Subcategory.objects.create(name="Jeans", category=pants)
        belts = Subcategory.objects.create(name="Belts", category=accessories)
        running_shoes = Subcategory.objects.create(name="Running", category=shoes)
        casual_shoes = Subcategory.objects.create(name="Casual", category=shoes)
        
        # Products with reliable image URLs
        products_data = [
            {
                "name": "Adidas Men's T-Shirt",
                "price": 29.99,
                "category": shirts,
                "subcategory": mens_shirts,
                "brand": "Adidas",
                "color": "Blue",
                "size": "M",
                "description": "Comfortable and stylish Adidas t-shirt for men, made from 100% cotton. Perfect for workouts or casual wear.",
                "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Puma Women's Top",
                "price": 25.99,
                "category": shirts,
                "subcategory": womens_shirts,
                "brand": "Puma",
                "color": "Red",
                "size": "S",
                "description": "Lightweight and breathable Puma top for women, perfect for workouts or casual wear. Moisture-wicking fabric keeps you dry.",
                "image_url": "https://images.unsplash.com/photo-1529903384028-929ae7b4a9f5?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Nike Men's Jeans",
                "price": 49.99,
                "category": pants,
                "subcategory": jeans,
                "brand": "Nike",
                "color": "Black",
                "size": "32",
                "description": "Slim fit jeans from Nike, made with stretch denim for comfort and style. Perfect for everyday wear.",
                "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Under Armour Belt",
                "price": 19.99,
                "category": accessories,
                "subcategory": belts,
                "brand": "Under Armour",
                "color": "Brown",
                "size": "L",
                "description": "Durable and adjustable belt from Under Armour, perfect for athletic or casual use. Genuine leather construction.",
                "image_url": "https://images.unsplash.com/photo-1591348131719-8c1a7b8a2f0b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Adidas Running Shoes",
                "price": 99.99,
                "category": shoes,
                "subcategory": running_shoes,
                "brand": "Adidas",
                "color": "Black",
                "description": "High-performance running shoes with cushioned soles for maximum comfort. Responsive boost technology for energy return.",
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Nike Casual Shoes",
                "price": 89.99,
                "category": shoes,
                "subcategory": casual_shoes,
                "brand": "Nike",
                "color": "White",
                "description": "Stylish and comfortable casual shoes from Nike, suitable for everyday wear. Air cushioning for all-day comfort.",
                "image_url": "https://images.unsplash.com/photo-1600269452121-4f2416e55c28?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "YoungLA Workout Shirt",
                "price": 24.99,
                "category": shirts,
                "subcategory": mens_shirts,
                "brand": "YoungLA",
                "color": "Gray",
                "size": "L",
                "description": "Performance shirt for gym workouts, made with moisture-wicking fabric. Flexible material allows full range of motion.",
                "image_url": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Puma Running Shoes",
                "price": 79.99,
                "category": shoes,
                "subcategory": running_shoes,
                "brand": "Puma",
                "color": "Red",
                "description": "Lightweight running shoes with excellent grip and cushioning. Breathable mesh upper keeps feet cool during runs.",
                "image_url": "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Under Armour Hoodie",
                "price": 59.99,
                "category": shirts,
                "subcategory": mens_shirts,
                "brand": "Under Armour",
                "color": "Black",
                "size": "XL",
                "description": "Warm and comfortable hoodie with moisture-wicking technology. Perfect for cool weather workouts or casual wear.",
                "image_url": "https://images.unsplash.com/photo-1521489878980-316c3a8f2a6a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "Nike Yoga Pants",
                "price": 39.99,
                "category": pants,
                "subcategory": jeans,
                "brand": "Nike",
                "color": "Purple",
                "size": "M",
                "description": "Flexible and comfortable yoga pants with four-way stretch. High-waisted design for support during workouts.",
                "image_url": "https://images.unsplash.com/photo-1588117305388-c2631a279f82?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
            }
        ]
        
        # Create products
        for product_data in products_data:
            # Create product without image first
            product = Product.objects.create(
                name=product_data["name"],
                price=decimal.Decimal(str(product_data["price"])),
                category=product_data["category"],
                subcategory=product_data.get("subcategory", None),
                brand=product_data["brand"],
                color=product_data["color"],
                size=product_data.get("size", None),
                description=product_data["description"]
            )
            
            # Download and save image using urllib
            image_url = product_data.get("image_url")
            if image_url:
                try:
                    # Create a context to ignore SSL certificate errors
                    context = ssl._create_unverified_context()
                    
                    # Set headers to avoid being blocked
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                    }
                    
                    req = Request(image_url, headers=headers)
                    with urlopen(req, context=context, timeout=10) as response:
                        if response.status == 200:
                            image_data = response.read()
                            image_io = BytesIO(image_data)
                            filename = f"{product.slug}.jpg"
                            product.image.save(filename, File(image_io))
                            product.save()
                            self.stdout.write(self.style.SUCCESS(f"Downloaded image for {product.name}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Failed to download image for {product.name} (Status: {response.status})"))
                except (URLError, HTTPError, TimeoutError, OSError) as e:
                    self.stdout.write(self.style.WARNING(f"Error downloading image for {product.name}: {e}"))
                time.sleep(1)  # Be gentle to servers
        
        self.stdout.write(self.style.SUCCESS('Successfully populated sample data'))