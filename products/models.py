from django.db import models

from products.filters import PRODUCT_FILTER_RULES, collect_parameter_values


class Category(models.Model):
    """A grouping a product belongs to. A product belongs to exactly one."""

    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-safe identifier used in filter querystrings.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """A label a product may carry. A product may carry any number."""

    name = models.CharField(max_length=50, unique=True)
    code = models.SlugField(
        max_length=50,
        unique=True,
        help_text="URL-safe identifier used in filter querystrings.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def with_related_objects(self):
        """Fetch category and tags up front so templates cannot trigger a
        query per row."""
        return self.select_related("category").prefetch_related("tags")

    def apply_filters(self, parameters, rules=PRODUCT_FILTER_RULES):
        """
        Narrow the queryset using the registered filter rules.

        Only registered parameters can reach the ORM: the loop walks the rule
        registry, not whatever the client happened to send.
        """
        queryset = self
        for parameter_name, rule in rules.items():
            values = collect_parameter_values(parameters, parameter_name)
            if not values:
                continue
            queryset = rule.apply(
                queryset, values if rule.accepts_multiple else values[0]
            )
        return queryset


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
