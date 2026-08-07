from django.contrib import admin

from products.models import Category, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    # Fills `code` in from `name` while typing, which matters when entering
    # the sample data by hand.
    prepopulated_fields = {"code": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "created_at")
    list_filter = ("category", "tags")
    search_fields = ("name", "description")
    # A two-pane widget beats a multi-select for assigning several tags.
    filter_horizontal = ("tags",)
    autocomplete_fields = ("category",)
