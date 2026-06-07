from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AttributeDefinition(models.Model):
    DATA_TYPE_CHOICES = (
        ('int', 'Integer'),
        ('float', 'Float'),
        ('string', 'String'),
        ('bool', 'Boolean'),
        ('range', 'Range'),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    data_type = models.CharField(max_length=10, choices=DATA_TYPE_CHOICES)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='attributes'
    )
    is_filterable = models.BooleanField(default=True)

    class Meta:
        db_table = 'attribute_definitions'
        unique_together = ('slug', 'category')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Platform(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'platforms'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    manufacturer = models.CharField(max_length=200, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    datasheet = models.FileField(upload_to='datasheets/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    compatible_platforms = models.ManyToManyField(
        Platform, blank=True, related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='attributes'
    )
    attribute = models.ForeignKey(
        AttributeDefinition, on_delete=models.CASCADE, related_name='values'
    )
    value_string = models.CharField(max_length=500, blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_min = models.FloatField(blank=True, null=True)
    value_max = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'product_attributes'
        unique_together = ('product', 'attribute')

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}"

    @property
    def display_value(self):
        if self.attribute.data_type == 'range':
            return f"{self.value_min} - {self.value_max}"
        elif self.attribute.data_type in ('int', 'float'):
            return str(self.value_number)
        elif self.attribute.data_type == 'bool':
            return 'Yes' if self.value_string == 'true' else 'No'
        return self.value_string or ''
