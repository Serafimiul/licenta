from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
)
from catalog.models import Product


def _is_admin(user) -> bool:
    return user.is_authenticated and getattr(user, 'role', None) == 'admin'


class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """GET /api/cart/ — get or create cart for authenticated user."""
        cart, _ = Cart.objects.prefetch_related(
            'items__product__category',
            'items__product__compatible_platforms',
        ).get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        """POST /api/cart/items/ — add item to cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)

        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        if quantity < 1:
            return Response(
                {'error': 'Quantity must be at least 1.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity > product.stock:
            return Response(
                {'error': f'Only {product.stock} items available in stock.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                return Response(
                    {'error': f'Only {product.stock} items available in stock.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['put'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """PUT /api/cart/items/{id}/ — update item quantity."""
        try:
            cart_item = CartItem.objects.select_related('product').get(
                id=item_id, cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = int(request.data.get('quantity', 1))
        if quantity < 1:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if quantity > cart_item.product.stock:
            return Response(
                {'error': f'Only {cart_item.product.stock} items available.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)/remove')
    def remove_item(self, request, item_id=None):
        """DELETE /api/cart/items/{id}/remove/ — remove item from cart."""
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        """DELETE /api/cart/clear/ — remove all items from cart."""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        GET /api/orders/
          - admin: every order in the system
          - client: only the caller's own orders
        """
        qs = Order.objects.select_related('user').prefetch_related('items__product')
        if not _is_admin(request.user):
            qs = qs.filter(user=request.user)
        serializer = OrderSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/orders/{id}/ — admin sees any; client sees own."""
        qs = Order.objects.select_related('user').prefetch_related('items__product')
        if not _is_admin(request.user):
            qs = qs.filter(user=request.user)
        try:
            order = qs.get(id=pk)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """
        PATCH /api/orders/{id}/ — admin-only status update.
        Body: { "status": "shipped" }
        """
        if not _is_admin(request.user):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            order = Order.objects.select_related('user').prefetch_related(
                'items__product'
            ).get(id=pk)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data['status']
        order.save(update_fields=['status'])

        return Response(OrderSerializer(order).data)

    def create(self, request):
        """POST /api/orders/ — create order from cart (atomic)."""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart = Cart.objects.prefetch_related('items__product').get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.items.select_related('product').all()
        if not cart_items.exists():
            return Response(
                {'error': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate stock availability
        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response(
                    {'error': f'Insufficient stock for "{item.product.name}". '
                              f'Available: {item.product.stock}, requested: {item.quantity}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Atomic transaction: create order, deduct stock, clear cart
        with transaction.atomic():
            total = sum(item.product.price * item.quantity for item in cart_items)

            order = Order.objects.create(
                user=request.user,
                total=total,
                shipping_name=serializer.validated_data['shipping_name'],
                shipping_address=serializer.validated_data['shipping_address'],
                shipping_city=serializer.validated_data['shipping_city'],
                shipping_zip=serializer.validated_data['shipping_zip'],
                shipping_country=serializer.validated_data['shipping_country'],
                notes=serializer.validated_data.get('notes', ''),
            )

            order_items = []
            for item in cart_items:
                order_items.append(OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price,
                ))
                # Deduct stock
                item.product.stock -= item.quantity
                item.product.save()

            OrderItem.objects.bulk_create(order_items)

            # Clear cart
            cart.items.all().delete()

        order = Order.objects.prefetch_related('items__product').get(id=order.id)
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
