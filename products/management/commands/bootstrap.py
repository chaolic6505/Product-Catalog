from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"


class Command(BaseCommand):
    """Prepare a working database: migrate, load sample data, ensure an admin."""

    help = (
        "Apply migrations, load the sample product data, and create an admin "
        "account if one does not already exist."
    )

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        call_command("migrate", verbosity=verbosity)
        call_command("loaddata", "sample_data", verbosity=verbosity)
        self.ensure_admin_user(verbosity)

    def ensure_admin_user(self, verbosity):
        user_model = get_user_model()
        if user_model.objects.filter(username=ADMIN_USERNAME).exists():
            if verbosity:
                self.stdout.write("Admin account already present, leaving it alone.")
            return

        user_model.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
        )
        if verbosity:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created admin account " f"({ADMIN_USERNAME} / {ADMIN_PASSWORD})."
                )
            )
