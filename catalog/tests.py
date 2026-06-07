from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Category, AttributeDefinition, Product, ProductAttribute


class AttributeRangeFilterTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Test Cat', slug='test-cat')
        self.attr = AttributeDefinition.objects.create(
            name='Range', slug='rng', data_type='int', category=self.cat,
        )
        self._mk('Low', 10)
        self._mk('Mid', 50)
        self._mk('High', 100)

    def _mk(self, name, num):
        p = Product.objects.create(
            name=name, slug=name.lower(), price=10, stock=1,
            category=self.cat, sku=f'SKU-{name}', manufacturer='M', is_active=True,
        )
        ProductAttribute.objects.create(product=p, attribute=self.attr, value_number=num)
        return p

    def _names(self, params):
        res = self.client.get('/api/products/', params)
        self.assertEqual(res.status_code, 200)
        return {item['name'] for item in res.json()['results']}

    def test_min_bound(self):
        self.assertEqual(self._names({'attr_rng_min': 50}), {'Mid', 'High'})

    def test_max_bound(self):
        self.assertEqual(self._names({'attr_rng_max': 50}), {'Low', 'Mid'})

    def test_both_bounds(self):
        self.assertEqual(self._names({'attr_rng_min': 20, 'attr_rng_max': 80}), {'Mid'})


class AttributeRangeOverlapFilterTest(TestCase):
    """range data_type: product [value_min, value_max] overlap with query bounds."""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Range Cat', slug='range-cat')
        self.attr = AttributeDefinition.objects.create(
            name='Span', slug='span', data_type='range', category=self.cat,
        )
        self._mk('A', 0, 30)
        self._mk('B', 40, 60)
        self._mk('C', 90, 120)

    def _mk(self, name, vmin, vmax):
        p = Product.objects.create(
            name=name, slug=name.lower(), price=10, stock=1,
            category=self.cat, sku=f'SKU-{name}', manufacturer='M', is_active=True,
        )
        ProductAttribute.objects.create(
            product=p, attribute=self.attr, value_min=vmin, value_max=vmax,
        )
        return p

    def _names(self, params):
        res = self.client.get('/api/products/', params)
        self.assertEqual(res.status_code, 200)
        return {item['name'] for item in res.json()['results']}

    def test_min_bound(self):
        # value_max >= 50 → B(60), C(120)
        self.assertEqual(self._names({'attr_span_min': 50}), {'B', 'C'})

    def test_max_bound(self):
        # value_min <= 50 → A(0), B(40)
        self.assertEqual(self._names({'attr_span_max': 50}), {'A', 'B'})

    def test_both_bounds(self):
        # overlap [35, 65] → only B
        self.assertEqual(self._names({'attr_span_min': 35, 'attr_span_max': 65}), {'B'})


class CompareEndpointPermissionTest(TestCase):
    """The compare action is a POST; it must stay open to anonymous users
    (IsAdminOrReadOnly would otherwise 403 every non-admin POST)."""

    def setUp(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Cmp Cat', slug='cmp-cat')
        self.p1 = Product.objects.create(
            name='P1', slug='p1', price=10, stock=1,
            category=self.cat, sku='SKU-P1', manufacturer='M', is_active=True,
        )
        self.p2 = Product.objects.create(
            name='P2', slug='p2', price=20, stock=1,
            category=self.cat, sku='SKU-P2', manufacturer='M', is_active=True,
        )

    def test_anonymous_can_compare(self):
        res = self.client.post(
            '/api/products/compare/', {'ids': [self.p1.id, self.p2.id]}, format='json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual({item['name'] for item in res.json()}, {'P1', 'P2'})
