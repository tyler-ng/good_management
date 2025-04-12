from rest_framework import serializers
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'image', 'is_active']
        extra_kwargs = {
            'slug': {'read_only': True},
        }


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value']


class VariantAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute_value.attribute.name', read_only=True)
    value = serializers.CharField(source='attribute_value.value', read_only=True)

    class Meta:
        model = VariantAttributeValue
        fields = ['id', 'attribute_value', 'attribute_name', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_values = VariantAttributeValueSerializer(many=True, read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price_adjustment', 'price', 'inventory', 'is_available', 'attribute_values']


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'user_name', 'rating', 'title', 'comment', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'is_approved': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'description', 'price',
            'compare_price', 'discount_percentage', 'category',
            'category_name', 'inventory', 'is_available',
            'is_featured', 'primary_image', 'images',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'slug': {'read_only': True},
        }

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductDetailSerializer(ProductSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['variants', 'reviews', 'average_rating']

    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        return ProductReviewSerializer(reviews, many=True).data

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0