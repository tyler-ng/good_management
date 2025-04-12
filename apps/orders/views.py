from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, Payment
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, PaymentSerializer
from apps.users.permissions import IsAdmin, IsOwnerOrAdmin

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_or_create_cart(self):
        try:
            return Cart.objects.get(user=self.request.user)
        except Cart.DoesNotExist:
            return Cart.objects.create(user=self.request.user)
    
    def list(self, request):
        """Get current user's cart"""
        cart = self.get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add an item to the cart"""
        cart = self.get_or_create_cart()
        serializer = CartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.validated_data['product']
            variant = serializer.validated_data.get('variant')
            quantity = serializer.validated_data.get('quantity', 1)
            
            # Check if item already exists in cart
            try:
                cart_item = CartItem.objects.get(
                    cart=cart, 
                    product=product,
                    variant=variant
                )
                # Update quantity
                cart_item.quantity += quantity
                cart_item.save()
            except CartItem.DoesNotExist:
                # Create new cart item
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    quantity=quantity
                )
            
            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update item quantity in cart"""
        cart = self.get_or_create_cart()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)
        
        if not item_id:
            return Response(
                {"detail": "Item ID is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                cart_item.delete()
            else:
                # Update quantity
                cart_item.quantity = quantity
                cart_item.save()
            
            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Item not found in cart."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        cart = self.get_or_create_cart()
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {"detail": "Item ID is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            cart_item.delete()
            
            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Item not found in cart."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self.get_or_create_cart()
        cart.items.all().delete()
        
        cart_serializer = self.get_serializer(cart)
        return Response(cart_serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {"detail": "Cannot create order from empty cart."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data, context={'request': request, 'cart': cart})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['pending', 'processing']:
            return Response(
                {"detail": "Only pending or processing orders can be cancelled."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response(
                {"detail": "Status is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if status_value not in dict(Order.STATUS_CHOICES).keys():
            return Response(
                {"detail": "Invalid status value."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = status_value
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=user)
    
    def create(self, request, *args, **kwargs):
        # Get order from request data
        order_id = request.data.get('order')
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found or does not belong to current user."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if order is already paid
        if order.payments.filter(status='completed').exists():
            return Response(
                {"detail": "This order has already been paid for."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process payment (this would normally integrate with a payment processor)
        # For now, we'll simulate a successful payment
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(status='completed')
        
        # Update order status
        order.status = 'processing'
        order.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)