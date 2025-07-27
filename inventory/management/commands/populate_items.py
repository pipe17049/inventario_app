"""
Management command to populate the database with sample data
"""
from django.core.management.base import BaseCommand
from inventory.models import Item


class Command(BaseCommand):
    help = 'Populate the database with sample inventory items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing items before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing items...')
            Item.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared all items')
            )

        # Sample data
        sample_items = [
            {
                'name': 'MacBook Pro 16"',
                'description': 'Apple MacBook Pro 16-inch with M2 Pro chip',
                'quantity': 15,
                'price': 2499.99,
                'category': 'Electronics'
            },
            {
                'name': 'Wireless Mouse',
                'description': 'Logitech MX Master 3 Wireless Mouse',
                'quantity': 50,
                'price': 99.99,
                'category': 'Electronics'
            },
            {
                'name': 'Programming Book',
                'description': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'quantity': 25,
                'price': 42.99,
                'category': 'Books'
            },
            {
                'name': 'Office Chair',
                'description': 'Ergonomic office chair with lumbar support',
                'quantity': 8,
                'price': 299.99,
                'category': 'Furniture'
            },
            {
                'name': 'Coffee Mug',
                'description': 'Ceramic coffee mug with company logo',
                'quantity': 100,
                'price': 12.99,
                'category': 'Other'
            },
            {
                'name': 'USB-C Cable',
                'description': 'USB-C to USB-C cable, 2 meters',
                'quantity': 200,
                'price': 19.99,
                'category': 'Electronics'
            },
            {
                'name': 'Notebook',
                'description': 'Moleskine classic notebook, lined pages',
                'quantity': 30,
                'price': 24.99,
                'category': 'Office Supplies'
            },
            {
                'name': 'Desk Lamp',
                'description': 'LED desk lamp with adjustable brightness',
                'quantity': 12,
                'price': 79.99,
                'category': 'Furniture'
            }
        ]

        created_count = 0
        for item_data in sample_items:
            try:
                item = Item(**item_data)
                item.save()
                created_count += 1
                self.stdout.write(f'Created: {item.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating {item_data["name"]}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} sample items'
            )
        )
