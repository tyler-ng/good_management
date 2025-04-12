from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
    ProductAttribute,
    ProductAttributeValue,
    VariantAttributeValue,
    ProductReview
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'title', 'comment', 'created_at')
    can_delete = False
    max_num = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'category', 'inventory', 'is_available', 'is_featured')
    list_filter = ('is_available', 'is_featured', 'category')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline, ProductReviewInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Categorization', {
            'fields': ('category',)
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price')
        }),
        ('Inventory', {
            'fields': ('inventory', 'is_available')
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        }),
    )


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('value',)


class VariantAttributeValueInline(admin.TabularInline):
    model = VariantAttributeValue
    extra = 1


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'sku', 'price_adjustment', 'inventory', 'is_available')
    list_filter = ('is_available', 'product')
    search_fields = ('name', 'sku', 'product__name')
    inlines = [VariantAttributeValueInline]


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('title', 'comment', 'user__email', 'product__name')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    approve_reviews.short_description = "Approve selected reviews"


# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)