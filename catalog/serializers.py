from rest_framework import serializers
from django.db import transaction
from .models import Category, AttributeDefinition, Product, ProductAttribute, Platform


class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image')


class CategorySerializer(serializers.ModelSerializer):
    children = CategoryChildSerializer(many=True, read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'parent_name',
                  'description', 'image', 'children')


class AttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeDefinition
        fields = ('id', 'name', 'slug', 'unit', 'data_type', 'category', 'is_filterable')


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name', 'slug')


class ProductAttributeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='attribute.name', read_only=True)
    slug = serializers.CharField(source='attribute.slug', read_only=True)
    unit = serializers.CharField(source='attribute.unit', read_only=True)
    data_type = serializers.CharField(source='attribute.data_type', read_only=True)
    display_value = serializers.CharField(read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ('id', 'name', 'slug', 'unit', 'data_type',
                  'value_string', 'value_number', 'value_min', 'value_max',
                  'display_value')


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    compatible_platforms = PlatformSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price', 'stock', 'image',
                  'manufacturer', 'sku', 'is_active', 'category_name',
                  'category_slug', 'compatible_platforms', 'created_at')


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    compatible_platforms = PlatformSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'price', 'stock',
                  'category', 'manufacturer', 'sku', 'image', 'datasheet',
                  'is_active', 'compatible_platforms', 'attributes', 'created_at')


class ProductWriteSerializer(serializers.ModelSerializer):
    """
    Admin write serializer for products.

    Accepts:
      - All scalar product fields (name, price, stock, etc.)
      - `platforms`: list of platform IDs → set on compatible_platforms M2M
      - `attributes`: dict {attribute_slug: value} → upserts ProductAttribute
        rows. Value type is interpreted from AttributeDefinition.data_type:
          * int / float       → numeric scalar
          * range             → [min, max] list/tuple
          * string / bool     → string
    """
    platforms = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.all(),
        many=True, required=False, write_only=True,
    )
    attributes = serializers.DictField(
        child=serializers.JSONField(),
        required=False, write_only=True,
    )
    # Make image truly optional (admin may keep the existing one).
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'price', 'stock',
            'category', 'manufacturer', 'sku', 'image', 'datasheet',
            'is_active', 'platforms', 'attributes',
        )
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
        }

    def to_internal_value(self, data):
        """
        When the request arrives via multipart/form-data (because of the image
        upload), nested fields come in as raw strings. JSON-decode `attributes`
        so the DictField sees a real dict.
        """
        import json
        if hasattr(data, '_mutable'):
            data._mutable = True
        attrs_raw = data.get('attributes')
        if isinstance(attrs_raw, str):
            try:
                data['attributes'] = json.loads(attrs_raw)
            except (ValueError, TypeError):
                data['attributes'] = {}
        return super().to_internal_value(data)

    def _extract_attributes(self, validated_data):
        """
        Pull attributes from validated_data first (JSON request path), then fall
        back to raw initial_data (multipart path, where DRF's DictField.get_value
        can't extract a single JSON-encoded blob and silently returns {}).
        """
        attrs = validated_data.pop('attributes', None)
        if attrs:
            return attrs
        raw = self.initial_data.get('attributes') if hasattr(self, 'initial_data') else None
        if isinstance(raw, str):
            import json
            try:
                return json.loads(raw)
            except (ValueError, TypeError):
                return {}
        if isinstance(raw, dict):
            return raw
        return {}

    @transaction.atomic
    def create(self, validated_data):
        platforms = validated_data.pop('platforms', [])
        attributes = self._extract_attributes(validated_data)
        product = Product.objects.create(**validated_data)
        product.compatible_platforms.set(platforms)
        self._upsert_attributes(product, attributes)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        platforms = validated_data.pop('platforms', None)
        attributes = self._extract_attributes(validated_data)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if platforms is not None:
            instance.compatible_platforms.set(platforms)
        if attributes:
            self._upsert_attributes(instance, attributes)
        return instance

    def _upsert_attributes(self, product: Product, attributes: dict) -> None:
        if not attributes:
            return
        defs = {
            d.slug: d for d in AttributeDefinition.objects.filter(
                category=product.category, slug__in=list(attributes.keys())
            )
        }
        for slug, raw_value in attributes.items():
            attr_def = defs.get(slug)
            if attr_def is None or raw_value in (None, ''):
                continue
            kwargs = {'product': product, 'attribute': attr_def}
            if attr_def.data_type == 'range' and isinstance(raw_value, (list, tuple)) \
                    and len(raw_value) == 2:
                kwargs['value_min'] = float(raw_value[0])
                kwargs['value_max'] = float(raw_value[1])
            elif attr_def.data_type in ('int', 'float'):
                try:
                    kwargs['value_number'] = float(raw_value)
                except (TypeError, ValueError):
                    continue
            else:
                kwargs['value_string'] = str(raw_value)

            ProductAttribute.objects.update_or_create(
                product=product, attribute=attr_def,
                defaults={k: v for k, v in kwargs.items()
                          if k not in ('product', 'attribute')},
            )

    def to_representation(self, instance):
        """Return the full read shape so the admin gets back what it just saved."""
        return ProductDetailSerializer(instance, context=self.context).data


class CategoryWriteSerializer(serializers.ModelSerializer):
    """Admin write serializer for categories."""

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'description', 'image')
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
        }

    def to_representation(self, instance):
        return CategorySerializer(instance, context=self.context).data
