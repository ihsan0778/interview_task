from django.core.management.base import BaseCommand
from product.models import Product, Category
import random
import string

class Command(BaseCommand):
    help = 'Generates dummy products based on input'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of dummy products to generate')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        categories = Category.objects.all()

        for _ in range(count):
            title = 'Dummy Product ' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            description = 'Description for ' + title
            price = round(random.uniform(10, 1000), 2)
            category = random.choice(categories)

            Product.objects.create(
                category=category,
                title=title,
                description=description,
                price=price
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {count} dummy products'))
