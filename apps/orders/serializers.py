from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment
from apps.products.models import Product, ProductVariant
from apps.products.serializers import ProductSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='variant',
        write_only=True,
        required=False,
        allow_null=True
    )
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'variant', 'variant_id', 'quantity', 'unit_price', 'total_price']

    def validate(self, data):
        product = data.get('product')
        variant = data.get('variant')
        quantity = data.get('quantity', 1)

        # Check if variant belongs to product
        if variant and variant.product.id != product.id:
            raise serializers.ValidationError("This variant does not belong to the selected product.")

        # Check if product or variant is available
        if not product.is_available:
            raise serializers.ValidationError("This product is not available.")

        if variant and not variant.is_available:
            raise serializers.ValidationError("This variant is not available.")

        # Check inventory
        available_inventory = variant.inventory if variant else product.inventory
        if quantity > available_inventory:
            raise serializers.ValidationError(f"Only {available_inventory} items available in stock.")

        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'variant_name', 'sku', 'unit_price', 'quantity', 'total_price']
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'first_name', 'last_name',
            'email', 'phone', 'address', 'city', 'state',
            'postal_code', 'country', 'status', 'shipping_method',
            'shipping_price', 'subtotal', 'tax', 'total',
            'tracking_number', 'notes', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'status', 'user', 'subtotal', 'total', 'created_at']

    def create(self, validated_data):
        # Get cart from context
        cart = self.context.get('cart')
        if not cart or not cart.items.exists():
            raise serializers.ValidationError("Cannot create order from empty cart.")

        # Calculate totals
        validated_data['subtotal'] = cart.total_price
        validated_data['total'] = validated_data['subtotal'] + validated_data.get('shipping_price',
                                                                                  0) + validated_data.get('tax', 0)

        # Set user if authenticated
        user = self.context.get('request').user
        if user.is_authenticated:
            validated_data['user'] = user

        # Create order
        order = Order.objects.create(**validated_data)

        # Create order items from cart items
        for cart_item in cart.items.all():
            product = cart_item.product
            variant = cart_item.variant

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                variant=variant,
                variant_name=variant.name if variant else '',
                sku=variant.sku if variant else product.sku,
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price
            )

        # Clear the cart
        cart.items.all().delete()

        return order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_method', 'transaction_id', 'amount', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, data):
        order = data.get('order')
        amount = data.get('amount')

        # Check if payment amount matches order total
        if order.total != amount:
            raise serializers.ValidationError("Payment amount must match order total.")

        # Check if order is already paid
        if order.payments.filter(status='completed').exists():
            raise serializers.ValidationError("This order has already been paid for.")

        return data