from django.contrib import admin
from .models import Category, MenuItem, Table, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_occupied_admin')
    
    def is_occupied_admin(self, obj):
        return obj.is_occupied
    is_occupied_admin.boolean = True
    is_occupied_admin.short_description = 'Occupied'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'waiter', 'is_active', 'is_paid', 'created_at', 'total_amount')
    list_filter = ('is_active', 'is_paid', 'created_at')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity', 'status')
    list_filter = ('status',)
