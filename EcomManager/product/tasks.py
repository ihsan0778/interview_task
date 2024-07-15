from celery import shared_task
from django.utils.crypto import get_random_string
from .models import Category, Product
from django.contrib.auth import get_user_model
User = get_user_model()
import random

@shared_task
def generate_dummy_data(num_categories, num_products):
    for _ in range(num_categories):
        category_name = get_random_string(length=10)
        category = Category.objects.create(name=category_name)
        
    for _ in range(num_products):
        title = get_random_string(length=10)
        description = get_random_string(length=50)
        price = round(random.uniform(10.0, 100.0), 2)
        Product.objects.create(
            category=category,
            title=title,
            description=description,
            price=price,
            status='draft',
            created_by=User.objects.first()  # Set to any user
        )
