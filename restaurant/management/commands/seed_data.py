from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from restaurant.models import Category, MenuItem, Table

class Command(BaseCommand):
    help = 'Seeds the database with initial Categories, MenuItems, and Users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Create Groups
        groups = ['Manager', 'Waiter', 'Kitchen']
        for g in groups:
            Group.objects.get_or_create(name=g)
        self.stdout.write('Created Groups')

        # Create Users
        users = {
            'manager': 'Manager',
            'waiter': 'Waiter',
            'kitchen': 'Kitchen'
        }
        
        for username, group_name in users.items():
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username=username, password='password123')
                g = Group.objects.get(name=group_name)
                u.groups.add(g)
                self.stdout.write(f'Created User: {username} (password123)')


        # defined categories and items
        data = {
            "Starter": ["Paneer Chilly", "Veg Manchurian", "Crispy Corn"],
            "Drink": ["Cold Coffee", "Fresh Lime Soda", "Lassi", "Water"],
            "Breads": ["Roti", "Butter Roti", "Naan", "Garlic Naan"],
            "Rice": ["Jeera Rice", "Steamed Rice", "Veg Biryani"],
            "Dal": ["Dal Fry", "Dal Tadka", "Dal Makhani"],
            "Main Course": ["Paneer Bhurji", "Paneer Butter Masala", "Mix Veg", "Malai Kofta"]
        }

        # Create Categories and Items
        for cat_name, items in data.items():
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(f'Created Category: {cat_name}')
            
            for item_name in items:
                # Assign arbitrary price for demo
                price = 100.00
                if "Paneer" in item_name: price = 250.00
                elif "Dal" in item_name: price = 180.00
                elif "Roti" in item_name: price = 20.00
                elif "Naan" in item_name: price = 40.00
                elif "Rice" in item_name: price = 150.00
                elif "Coffee" in item_name: price = 120.00

                MenuItem.objects.get_or_create(category=category, name=item_name, defaults={'price': price})
        
        # Create some tables
        for i in range(1, 11):
            Table.objects.get_or_create(number=i)
        self.stdout.write('Created Tables 1-10')

        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
