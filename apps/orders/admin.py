from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'unit_price', 'total_price')
    can_delete = False

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username', 'session_id')
    readonly_fields = ('total_price', 'total_items')
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'variant', 'variant_name', 'sku', 'unit_price', 'quantity', 'total_price')
    can_delete = False

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_method', 'transaction_id', 'amount', 'status', 'created_at')
    can_delete = False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'full_name', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email', 'first_name', 'last_name', 'email')
    readonly_fields = ('order_number', 'subtotal', 'total', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Information', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country', 'shipping_method', 'shipping_price', 'tracking_number')
        }),
        ('Order Details', {
            'fields': ('subtotal', 'tax', 'total', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [OrderItemInline, PaymentInline]
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Customer Name"

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')

# Register models
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)