from django.views.generic import ListView

from products.models import Category, Product, Tag


class ProductListView(ListView):
    """
    The catalog page.

    Holds no filtering logic of its own: the queryset applies the registered
    filter rules, so adding a filter never touches this class.
    """

    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.with_related_objects().apply_filters(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()
        context["selected_search"] = self.request.GET.get("search", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_tags"] = self.request.GET.getlist("tags")
        context["filter_querystring"] = self.build_filter_querystring()
        return context

    def build_filter_querystring(self):
        """The active query parameters minus `page`, so that pagination links
        preserve the filters instead of resetting them."""
        parameters = self.request.GET.copy()
        parameters.pop("page", None)
        return parameters.urlencode()
