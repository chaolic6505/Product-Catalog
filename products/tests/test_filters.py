from decimal import Decimal

from django.test import TestCase

from products.models import Category, Product, Tag


class ApplyFiltersTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.audio = Category.objects.create(name="Audio", code="audio")
        cls.video = Category.objects.create(name="Video", code="video")

        cls.wireless = Tag.objects.create(name="Wireless", code="wireless")
        cls.portable = Tag.objects.create(name="Portable", code="portable")

        cls.travel_headphones = cls.build_product(
            name="Travel Headphones",
            description="Wireless over-ear headphones for the commute",
            category=cls.audio,
            tags=[cls.wireless, cls.portable],
        )
        cls.desk_speaker = cls.build_product(
            name="Desk Speaker",
            description="Wireless shelf speaker for a small room",
            category=cls.audio,
            tags=[cls.wireless],
        )
        cls.hdmi_cable = cls.build_product(
            name="HDMI Cable",
            description="Braided cable, two metres",
            category=cls.video,
            tags=[],
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

    def filtered_names(self, parameters):
        """Sorted names of the products surviving the given parameters."""
        return sorted(
            product.name for product in Product.objects.apply_filters(parameters)
        )

    def test_no_parameters_returns_every_product(self):
        """An empty parameter set narrows nothing."""
        self.assertEqual(
            self.filtered_names({}),
            ["Desk Speaker", "HDMI Cable", "Travel Headphones"],
        )

    def test_search_matches_the_description_case_insensitively(self):
        """A lowercase term matches a capitalised word in the description."""
        self.assertEqual(
            self.filtered_names({"search": "wireless"}),
            ["Desk Speaker", "Travel Headphones"],
        )

    def test_search_matches_a_substring(self):
        """The search is a substring match, not a whole-word match."""
        self.assertEqual(
            self.filtered_names({"search": "commut"}), ["Travel Headphones"]
        )

    def test_search_does_not_look_at_the_product_name(self):
        """Only the description is searched, per the requirement."""
        self.assertEqual(self.filtered_names({"search": "HDMI"}), [])

    def test_the_category_filter_matches_on_code(self):
        """Categories are selected by their code, not their primary key."""
        self.assertEqual(
            self.filtered_names({"category": "audio"}),
            ["Desk Speaker", "Travel Headphones"],
        )

    def test_a_single_tag_returns_every_product_carrying_it(self):
        """One tag behaves as a plain membership filter."""
        self.assertEqual(
            self.filtered_names({"tags": ["wireless"]}),
            ["Desk Speaker", "Travel Headphones"],
        )

    def test_several_tags_require_all_of_them(self):
        """A product carrying only one of the selected tags is excluded."""
        self.assertEqual(
            self.filtered_names({"tags": ["wireless", "portable"]}),
            ["Travel Headphones"],
        )

    def test_repeating_a_tag_does_not_duplicate_rows(self):
        """De-duplicating the incoming values keeps the result set clean."""
        self.assertEqual(
            self.filtered_names({"tags": ["wireless", "wireless"]}),
            ["Desk Speaker", "Travel Headphones"],
        )

    def test_search_and_category_combine(self):
        """Two filters narrow the result set together."""
        self.assertEqual(
            self.filtered_names({"search": "shelf", "category": "audio"}),
            ["Desk Speaker"],
        )

    def test_all_three_filters_combine(self):
        """Search, category and tags apply simultaneously."""
        self.assertEqual(
            self.filtered_names(
                {
                    "search": "wireless",
                    "category": "audio",
                    "tags": ["wireless", "portable"],
                }
            ),
            ["Travel Headphones"],
        )

    def test_a_combination_that_matches_nothing_returns_nothing(self):
        """Contradictory filters produce an empty result set, not an error."""
        self.assertEqual(
            self.filtered_names({"search": "wireless", "category": "video"}), []
        )

    def test_a_blank_parameter_is_ignored(self):
        """An empty search box must not filter on the empty string."""
        self.assertEqual(
            self.filtered_names({"search": ""}),
            ["Desk Speaker", "HDMI Cable", "Travel Headphones"],
        )

    def test_a_whitespace_only_parameter_is_ignored(self):
        """Whitespace is trimmed before the value is considered."""
        self.assertEqual(
            self.filtered_names({"search": "   "}),
            ["Desk Speaker", "HDMI Cable", "Travel Headphones"],
        )

    def test_an_unregistered_parameter_is_ignored(self):
        """The loop walks the rule registry, so unknown parameters cannot
        reach the ORM."""
        self.assertEqual(
            self.filtered_names({"price": "99.00", "order_by": "id"}),
            ["Desk Speaker", "HDMI Cable", "Travel Headphones"],
        )

    def test_the_result_is_still_a_queryset(self):
        """apply_filters is chainable, so callers can keep refining."""
        result = Product.objects.apply_filters({"category": "audio"}).order_by("-name")
        self.assertEqual(
            [product.name for product in result],
            ["Travel Headphones", "Desk Speaker"],
        )


class WithRelatedObjectsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Audio", code="audio")
        tag = Tag.objects.create(name="Wireless", code="wireless")
        for index in range(5):
            product = Product.objects.create(
                name=f"Speaker {index}",
                description="Wireless shelf speaker",
                price=Decimal("99.00"),
                category=category,
            )
            product.tags.set([tag])

    def test_related_objects_are_fetched_without_a_query_per_row(self):
        """One query for the products and their categories, one for the tags,
        no matter how many products there are."""
        with self.assertNumQueries(2):
            for product in Product.objects.with_related_objects():
                product.category.name
                [tag.name for tag in product.tags.all()]
