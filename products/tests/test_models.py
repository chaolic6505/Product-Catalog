from decimal import Decimal

from django.db.models import ProtectedError
from django.test import TestCase

from products.models import Category, Product, Tag


class CategoryTests(TestCase):
    def test_a_category_renders_as_its_name(self):
        """str(category) is the category name."""
        category = Category.objects.create(name="Audio", code="audio")
        self.assertEqual(str(category), "Audio")

    def test_categories_come_back_alphabetically(self):
        """Meta.ordering sorts categories by name regardless of insert order."""
        Category.objects.create(name="Video", code="video")
        Category.objects.create(name="Audio", code="audio")
        self.assertEqual(
            [category.name for category in Category.objects.all()],
            ["Audio", "Video"],
        )


class TagTests(TestCase):
    def test_a_tag_renders_as_its_name(self):
        """str(tag) is the tag name."""
        tag = Tag.objects.create(name="Wireless", code="wireless")
        self.assertEqual(str(tag), "Wireless")

    def test_tags_come_back_alphabetically(self):
        """Meta.ordering sorts tags by name regardless of insert order."""
        Tag.objects.create(name="Wireless", code="wireless")
        Tag.objects.create(name="Portable", code="portable")
        self.assertEqual(
            [tag.name for tag in Tag.objects.all()],
            ["Portable", "Wireless"],
        )


class ProductTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Audio", code="audio")
        cls.wireless = Tag.objects.create(name="Wireless", code="wireless")
        cls.portable = Tag.objects.create(name="Portable", code="portable")

    def create_product(self, name="Headphones"):
        return Product.objects.create(
            name=name,
            description="Over-ear noise cancelling headphones",
            price=Decimal("249.99"),
            category=self.category,
        )

    def test_a_product_renders_as_its_name(self):
        """str(product) is the product name."""
        self.assertEqual(str(self.create_product()), "Headphones")

    def test_a_product_can_carry_several_tags(self):
        """The tags relation accepts more than one tag."""
        product = self.create_product()
        product.tags.set([self.wireless, self.portable])
        self.assertEqual(product.tags.count(), 2)

    def test_a_product_may_have_no_tags(self):
        """The tags relation is optional."""
        self.assertEqual(self.create_product().tags.count(), 0)

    def test_products_are_reachable_from_their_category(self):
        """related_name exposes the reverse accessor category.products."""
        product = self.create_product()
        self.assertIn(product, self.category.products.all())

    def test_products_are_reachable_from_their_tag(self):
        """related_name exposes the reverse accessor tag.products."""
        product = self.create_product()
        product.tags.set([self.wireless])
        self.assertIn(product, self.wireless.products.all())

    def test_deleting_a_category_that_still_has_products_is_refused(self):
        """PROTECT stops a category delete from cascading into its products."""
        self.create_product()
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_the_price_keeps_its_exact_decimal_value(self):
        """DecimalField stores currency without binary rounding error."""
        product = self.create_product()
        product.refresh_from_db()
        self.assertEqual(product.price, Decimal("249.99"))
