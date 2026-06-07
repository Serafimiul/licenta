from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from catalog.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_detail', 'quantity', 'subtotal')
        extra_kwargs = {'product': {'write_only': False}}


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'created_at')


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default='Deleted')
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'total', 'shipping_name', 'shipping_address',
                  'shipping_city', 'shipping_zip', 'shipping_country', 'notes',
                  'items', 'user_username', 'user_email', 'created_at')
        read_only_fields = ('id', 'total', 'items', 'created_at',
                            'user_username', 'user_email')


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Admin-only: change an order's status."""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)


class OrderCreateSerializer(serializers.Serializer):
    shipping_name = serializers.CharField(max_length=200)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_zip = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default='Romania')
    notes = serializers.CharField(required=False, allow_blank=True, default='')
