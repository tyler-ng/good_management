from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, Order, Payment
from apps.products.models import Product, ProductVariant


@receiver(post_save, sender=OrderItem)
def update_inventory(sender, instance, created, **kwargs):
    """
    Update product or variant inventory when an order item is created
    """
    if created:
        if instance.variant:
            # Update variant inventory
            variant = instance.variant
            if variant.inventory >= instance.quantity:
                variant.inventory -= instance.quantity
                variant.save(update_fields=['inventory'])

                # Also update product inventory if needed
                product = variant.product
                if product.inventory >= instance.quantity:
                    product.inventory -= instance.quantity
                    product.save(update_fields=['inventory'])
        else:
            # Update product inventory
            product = instance.product
            if product and product.inventory >= instance.quantity:
                product.inventory -= instance.quantity
                product.save(update_fields=['inventory'])


@receiver(post_save, sender=Payment)
def update_order_status(sender, instance, created, **kwargs):
    """
    Update order status when a payment is completed
    """
    if instance.status == 'completed':
        order = instance.order
        if order.status == 'pending':
            order.status = 'processing'
            order.save(update_fields=['status'])


@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Send notifications when an order is created or its status changes
    This would connect to an email service or notification system
    """
    if created:
        # Send order confirmation to customer
        # This is a placeholder for actual email sending logic
        print(f"New order {instance.order_number} created for {instance.email}")
    else:
        # Send order status update to customer
        # This is a placeholder for actual email sending logic
        print(f"Order {instance.order_number} status updated to {instance.status}")