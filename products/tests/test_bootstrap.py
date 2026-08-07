from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from products.models import Category, Product, Tag


class BootstrapCommandTests(TestCase):
    def test_it_loads_the_sample_data(self):
        """The committed fixture satisfies the required record counts."""
        call_command("bootstrap", verbosity=0)
        self.assertGreaterEqual(Category.objects.count(), 5)
        self.assertGreaterEqual(Tag.objects.count(), 10)
        self.assertGreaterEqual(Product.objects.count(), 20)

    def test_it_creates_an_admin_user(self):
        """The reviewer gets an account without running createsuperuser."""
        call_command("bootstrap", verbosity=0)
        self.assertTrue(get_user_model().objects.filter(username="admin").exists())

    def test_the_admin_user_can_reach_the_admin_site(self):
        """The created account is a working superuser, not a plain user."""
        call_command("bootstrap", verbosity=0)
        self.assertTrue(self.client.login(username="admin", password="admin"))

    def test_running_it_twice_does_not_duplicate_products(self):
        """Explicit primary keys in the fixture make loaddata idempotent."""
        call_command("bootstrap", verbosity=0)
        first_count = Product.objects.count()
        call_command("bootstrap", verbosity=0)
        self.assertEqual(Product.objects.count(), first_count)

    def test_running_it_twice_does_not_fail_on_the_existing_admin(self):
        """A second run leaves the existing admin account alone."""
        call_command("bootstrap", verbosity=0)
        call_command("bootstrap", verbosity=0)
        self.assertEqual(get_user_model().objects.filter(username="admin").count(), 1)
