from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import ProductImage, ProductReview, Product

@receiver(post_save, sender=ProductImage)
def set_primary_image(sender, instance, created, **kwargs):
    """Set the first uploaded image as primary if no primary image exists"""
    if created and instance.is_primary:
        # If this new image is marked as primary, unmark others
        ProductImage.objects.filter(
            product=instance.product,
            is_primary=True
        ).exclude(id=instance.id).update(is_primary=False)
    elif created and not ProductImage.objects.filter(product=instance.product, is_primary=True).exists():
        # If no primary image exists, make this one primary
        instance.is_primary = True
        instance.save(update_fields=['is_primary'])

@receiver(post_save, sender=ProductReview)
def update_product_rating(sender, instance, **kwargs):
    """Update product's average rating when a new review is added or a review is updated"""
    # We'll actually implement this using a property in the Product model
    # to calculate average rating on the fly, so this is a placeholder
    pass

@receiver(post_save, sender=Product)
def check_product_availability(sender, instance, **kwargs):
    """
    Automatically mark products as unavailable when inventory is 0
    """
    if instance.inventory <= 0 and instance.is_available:
        instance.is_available = False
        instance.save(update_fields=['is_available'])
    elif instance.inventory > 0 and not instance.is_available:
        # Optionally auto-mark products as available when inventory increases
        # Uncomment if this behavior is desired
        # instance.is_available = True
        # instance.save(update_fields=['is_available'])
        pass