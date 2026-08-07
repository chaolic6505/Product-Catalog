from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, Tag


class AdminSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = get_user_model().objects.create_superuser(
            username="tester", email="tester@example.com", password="password"
        )
        cls.category = Category.objects.create(name="Audio", code="audio")
        cls.tag = Tag.objects.create(name="Wireless", code="wireless")
        product = Product.objects.create(
            name="Headphones",
            description="Over-ear noise cancelling headphones",
            price=Decimal("249.99"),
            category=cls.category,
        )
        product.tags.set([cls.tag])

    def setUp(self):
        self.client.force_login(self.staff_user)

    def test_the_category_list_page_loads(self):
        """Categories are registered and their changelist renders."""
        response = self.client.get(reverse("admin:products_category_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_the_tag_list_page_loads(self):
        """Tags are registered and their changelist renders."""
        response = self.client.get(reverse("admin:products_tag_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_the_product_list_page_loads(self):
        """Products are registered and their changelist renders."""
        response = self.client.get(reverse("admin:products_product_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_the_product_add_page_loads(self):
        """The product form renders, which exercises autocomplete and
        filter_horizontal configuration."""
        response = self.client.get(reverse("admin:products_product_add"))
        self.assertEqual(response.status_code, 200)

    def test_products_can_be_searched_by_description(self):
        """search_fields covers description, so the admin search box finds it."""
        url = reverse("admin:products_product_changelist")
        response = self.client.get(url, {"q": "noise cancelling"})
        self.assertContains(response, "Headphones")
