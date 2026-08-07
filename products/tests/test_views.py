from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, Tag


class ProductListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.audio = Category.objects.create(name="Audio", code="audio")
        cls.video = Category.objects.create(name="Video", code="video")
        cls.wireless = Tag.objects.create(name="Wireless", code="wireless")
        cls.portable = Tag.objects.create(name="Portable", code="portable")

        cls.travel_headphones = cls.build_product(
            "Travel Headphones",
            "Wireless over-ear headphones for the commute",
            cls.audio,
            [cls.wireless, cls.portable],
        )
        cls.desk_speaker = cls.build_product(
            "Desk Speaker",
            "Wireless shelf speaker for a small room",
            cls.audio,
            [cls.wireless],
        )
        cls.hdmi_cable = cls.build_product(
            "HDMI Cable", "Braided cable, two metres", cls.video, []
        )

    @classmethod
    def build_product(cls, name, description, category, tags):
        product = Product.objects.create(
            name=name,
            description=description,
            price=Decimal("99.00"),
            category=category,
        )
        product.tags.set(tags)
        return product

    @property
    def url(self):
        return reverse("products:product-list")

    def listed_names(self, response):
        return sorted(product.name for product in response.context["products"])

    def test_the_page_loads(self):
        """The product list is served at the site root."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_it_uses_the_product_list_template(self):
        """The expected template renders the page."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "products/product_list.html")

    def test_it_lists_every_product_when_unfiltered(self):
        """With no query parameters the whole catalog is shown."""
        response = self.client.get(self.url)
        self.assertEqual(
            self.listed_names(response),
            ["Desk Speaker", "HDMI Cable", "Travel Headphones"],
        )

    def test_it_filters_by_search_term(self):
        """The search box narrows the list by description."""
        response = self.client.get(self.url, {"search": "commute"})
        self.assertEqual(self.listed_names(response), ["Travel Headphones"])

    def test_it_filters_by_category(self):
        """The category dropdown narrows the list."""
        response = self.client.get(self.url, {"category": "video"})
        self.assertEqual(self.listed_names(response), ["HDMI Cable"])

    def test_it_requires_every_selected_tag(self):
        """Selecting two tags returns only products carrying both."""
        response = self.client.get(self.url, {"tags": ["wireless", "portable"]})
        self.assertEqual(self.listed_names(response), ["Travel Headphones"])

    def test_it_combines_search_category_and_tags(self):
        """All three controls apply at once."""
        response = self.client.get(
            self.url,
            {"search": "wireless", "category": "audio", "tags": ["wireless"]},
        )
        self.assertEqual(
            self.listed_names(response), ["Desk Speaker", "Travel Headphones"]
        )

    def test_it_offers_every_category_and_tag_as_a_choice(self):
        """The controls are populated from the database, not hard-coded."""
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["categories"]), [self.audio, self.video])
        self.assertEqual(list(response.context["tags"]), [self.portable, self.wireless])

    def test_it_remembers_the_submitted_filters(self):
        """Selections survive the round trip so the form stays populated."""
        response = self.client.get(
            self.url,
            {"search": "wireless", "category": "audio", "tags": ["wireless"]},
        )
        self.assertEqual(response.context["selected_search"], "wireless")
        self.assertEqual(response.context["selected_category"], "audio")
        self.assertEqual(response.context["selected_tags"], ["wireless"])

    def test_the_submitted_search_term_appears_in_the_input(self):
        """The rendered input carries the previous value."""
        response = self.client.get(self.url, {"search": "wireless"})
        self.assertContains(response, 'value="wireless"')

    def test_it_reports_when_nothing_matches(self):
        """An empty result set shows a message rather than a blank page."""
        response = self.client.get(self.url, {"search": "nothing matches this"})
        self.assertEqual(self.listed_names(response), [])
        self.assertContains(response, "No products match these filters.")

    def test_the_pagination_querystring_drops_the_page_parameter(self):
        """Page links carry the active filters but not the old page number."""
        response = self.client.get(self.url, {"search": "wireless", "page": "1"})
        self.assertIn("search=wireless", response.context["filter_querystring"])
        self.assertNotIn("page=", response.context["filter_querystring"])


class ProductListPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Audio", code="audio")
        for index in range(12):
            Product.objects.create(
                name=f"Speaker {index:02d}",
                description="Wireless shelf speaker",
                price=Decimal("99.00"),
                category=category,
            )

    def test_the_first_page_holds_ten_products(self):
        """paginate_by caps each page at ten rows."""
        response = self.client.get(reverse("products:product-list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["products"]), 10)

    def test_the_second_page_holds_the_remainder(self):
        """The twelfth and eleventh products fall onto page two."""
        response = self.client.get(reverse("products:product-list"), {"page": "2"})
        self.assertEqual(len(response.context["products"]), 2)
