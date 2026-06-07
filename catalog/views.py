from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Q

from .models import Category, AttributeDefinition, Product, ProductAttribute, Platform
from .recommender import recommend_for
from .serializers import (
    CategorySerializer,
    CategoryWriteSerializer,
    AttributeDefinitionSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer,
    PlatformSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CategoryWriteSerializer
        return CategorySerializer

    def get_queryset(self):
        return Category.objects.select_related('parent').prefetch_related('children')

    def list(self, request, *args, **kwargs):
        # Return tree structure: only top-level categories with nested children.
        queryset = self.get_queryset().filter(parent__isnull=True)
        serializer = CategorySerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='flat',
            permission_classes=[permissions.AllowAny])
    def flat(self, request):
        """All categories as a flat list (admin form needs this)."""
        qs = self.get_queryset()
        return Response(CategorySerializer(qs, many=True).data)

    @action(detail=True, methods=['get'], url_path='attributes',
            permission_classes=[permissions.AllowAny])
    def attributes(self, request, slug=None):
        category = self.get_object()
        attrs = AttributeDefinition.objects.filter(
            category=category, is_filterable=True
        )
        serializer = AttributeDefinitionSerializer(attrs, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProductWriteSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def _is_admin_user(self) -> bool:
        user = self.request.user
        return user.is_authenticated and getattr(user, 'role', None) == 'admin'

    def get_queryset(self):
        # Admins see every product (active or not) so they can edit and
        # toggle visibility; everyone else only sees active products.
        if self._is_admin_user():
            queryset = Product.objects.all().select_related('category')
        else:
            queryset = Product.objects.filter(is_active=True).select_related('category')

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'attributes__attribute',
                'compatible_platforms',
            )
        else:
            queryset = queryset.prefetch_related('compatible_platforms')

        # Filter by category slug
        category_slug = self.request.query_params.get('category')
        if category_slug:
            # Include products from subcategories too
            try:
                category = Category.objects.get(slug=category_slug)
                descendant_ids = self._get_descendant_ids(category)
                queryset = queryset.filter(category_id__in=descendant_ids)
            except Category.DoesNotExist:
                queryset = queryset.none()

        # Price filters
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        # Platform filter
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(compatible_platforms__slug=platform)

        # Dynamic attribute filtering.
        #   Numeric/range:  attr_<slug>_min=<v>  and/or  attr_<slug>_max=<v>
        #   String/bool:    attr_<slug>=<v>      (exact match)
        for param, value in self.request.query_params.items():
            if not param.startswith('attr_') or value in ('', None):
                continue
            key = param[5:]  # strip 'attr_'
            bound = None
            if key.endswith('_min'):
                bound, slug = 'min', key[:-4]
            elif key.endswith('_max'):
                bound, slug = 'max', key[:-4]
            else:
                slug = key

            attr_def = AttributeDefinition.objects.filter(slug=slug).first()
            if attr_def is None:
                continue

            if attr_def.data_type in ('int', 'float'):
                try:
                    num = float(value)
                except (TypeError, ValueError):
                    continue
                if bound == 'min':
                    queryset = queryset.filter(
                        attributes__attribute=attr_def, attributes__value_number__gte=num)
                elif bound == 'max':
                    queryset = queryset.filter(
                        attributes__attribute=attr_def, attributes__value_number__lte=num)
                else:
                    queryset = queryset.filter(
                        attributes__attribute=attr_def, attributes__value_number=num)
            elif attr_def.data_type == 'range':
                try:
                    num = float(value)
                except (TypeError, ValueError):
                    continue
                if bound == 'min':
                    queryset = queryset.filter(
                        attributes__attribute=attr_def, attributes__value_max__gte=num)
                elif bound == 'max':
                    queryset = queryset.filter(
                        attributes__attribute=attr_def, attributes__value_min__lte=num)
                else:
                    queryset = queryset.filter(
                        attributes__attribute=attr_def,
                        attributes__value_min__lte=num, attributes__value_max__gte=num)
            elif bound is None:
                # string / bool exact match (single key only)
                queryset = queryset.filter(
                    attributes__attribute=attr_def, attributes__value_string__iexact=value)

        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed_orderings = ('price', '-price', 'name', '-name', 'created_at', '-created_at')
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)

        return queryset.distinct()

    def _get_descendant_ids(self, category):
        """Recursively get all descendant category IDs including self."""
        ids = [category.id]
        for child in category.children.all():
            ids.extend(self._get_descendant_ids(child))
        return ids

    @action(detail=False, methods=['post'], url_path='compare',
            permission_classes=[permissions.AllowAny])
    def compare(self, request):
        ids = request.data.get('ids', [])
        if not ids or len(ids) < 2:
            return Response(
                {'error': 'Provide at least 2 product IDs.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(ids) > 5:
            return Response(
                {'error': 'Maximum 5 products can be compared.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(id__in=ids, is_active=True).prefetch_related(
            'attributes__attribute', 'compatible_platforms'
        ).select_related('category')

        if products.count() < 2:
            return Response(
                {'error': 'Not enough valid products found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductDetailSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='recommendations',
            permission_classes=[permissions.AllowAny])
    def recommendations(self, request, slug=None):
        """
        Content-based vector-similarity recommendations, blended with a
        behavior-based popularity signal (order frequency).
        See `catalog/recommender.py` for the algorithm.
        """
        product = self.get_object()
        try:
            limit = int(request.query_params.get('limit', 4))
        except (TypeError, ValueError):
            limit = 4
        limit = max(1, min(limit, 12))

        recommendations = recommend_for(product, limit=limit)
        serializer = ProductListSerializer(recommendations, many=True,
                                           context={'request': request})
        return Response(serializer.data)


class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
