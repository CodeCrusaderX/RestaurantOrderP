from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # Optional: image = models.ImageField(...) but keeping it simple for now

    def __str__(self):
        return self.name

class Table(models.Model):
    number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Table {self.number}"

    @property
    def is_occupied(self):
        return self.orders.filter(is_active=True).exists()

class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) # Active until bill is cleared
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - Table {self.table.number}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('preparing', 'Preparing'),
        ('prepared', 'Prepared'),
        ('delivered', 'Delivered'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.item.name} ({self.status})"

    @property
    def subtotal(self):
        return self.item.price * self.quantity
