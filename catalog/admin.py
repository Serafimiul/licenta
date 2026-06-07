from django.contrib import admin
from .models import Category, AttributeDefinition, Product, ProductAttribute, Platform


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    list_filter = ('parent',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AttributeDefinition)
class AttributeDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'data_type', 'unit', 'is_filterable')
    list_filter = ('category', 'data_type', 'is_filterable')
    search_fields = ('name', 'slug')


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'manufacturer', 'compatible_platforms')
    search_fields = ('name', 'sku', 'manufacturer', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductAttributeInline]
    filter_horizontal = ('compatible_platforms',)


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
