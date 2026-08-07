# Product Catalog

A Django project modelling products, categories, and tags, with a page that
searches products by description and filters them by category and tags. All
three controls combine.

Repository: <https://github.com/chaolic6505/Product-Catalog>

## Requirements

- Python 3.11 or newer
- No database server: the project uses SQLite

## Setup

```bash
git clone https://github.com/chaolic6505/Product-Catalog.git
cd Product-Catalog
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py bootstrap
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

`bootstrap` applies migrations, loads the sample data fixture, and creates an
admin account if one does not exist. It is safe to run more than once.

To do the same steps manually:

```bash
python manage.py migrate
python manage.py loaddata sample_data
python manage.py createsuperuser
```

### Admin

<http://127.0.0.1:8000/admin/> — username `admin`, password `admin`.

These credentials are hardcoded in `products/management/commands/bootstrap.py`
as a convenience for reviewing a throwaway local database.

## Running the tests

```bash
python manage.py test
```

## Sample data

`products/fixtures/sample_data.json` contains 5 categories, 10 tags, and 20
products, entered through the Django admin interface and exported with
`dumpdata`. The SQLite database file itself is not committed.

## Assumptions

- Search covers the description only, not the product name, per the wording
  "search products by description".
- A product belongs to exactly one category, so `category` is a foreign key
  rather than a many-to-many relation.
- Deleting a category that still has products is refused (`on_delete=PROTECT`)
  rather than cascading.
- Selecting multiple tags means all of them, not any of them: each selected tag
  narrows the results further.
- Blank and whitespace-only parameters are ignored rather than filtered on.

## Notes on AI assistance

AI assistance was used while building this project: the models,
admin configuration, filter layer, catalog view and template, and the
`bootstrap` management command were planned with AI assistance, test-first, and
reviewed by the author.
