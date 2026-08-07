"""
Declarative filtering for product queries.

A filter rule knows how to apply one query parameter to a queryset. Rules are
registered in PRODUCT_FILTER_RULES, so adding a filter is a one-line change
there rather than a new branch in a view.

Rules are objects rather than a plain field-to-lookup mapping because not every
filter is expressible as a single lookup — see MatchesAll.
"""


class FilterRule:
    """One way of applying a single query parameter to a queryset."""

    accepts_multiple = False

    def __init__(self, field_lookup):
        self.field_lookup = field_lookup

    def apply(self, queryset, value):
        raise NotImplementedError


class ContainsText(FilterRule):
    """Case-insensitive substring match on a text field."""

    def apply(self, queryset, value):
        return queryset.filter(**{f"{self.field_lookup}__icontains": value})


class ExactMatch(FilterRule):
    """Exact match on a single field."""

    def apply(self, queryset, value):
        return queryset.filter(**{self.field_lookup: value})


class MatchesAll(FilterRule):
    """
    Every selected value must be present on the object.

    Each value gets its own .filter() call, and each call adds its own SQL
    JOIN. That is what produces AND semantics: the first JOIN is constrained to
    the first tag, the second to the second, so only a product carrying both
    survives both constraints.

    The single-JOIN alternative, .filter(tags__code__in=values), means OR
    instead, and emits one row per matching tag — which is why that form needs
    a .distinct() call and this one does not.
    """

    accepts_multiple = True

    def apply(self, queryset, values):
        for value in values:
            queryset = queryset.filter(**{self.field_lookup: value})
        return queryset


PRODUCT_FILTER_RULES = {
    "search": ContainsText("description"),
    "category": ExactMatch("category__code"),
    "tags": MatchesAll("tags__code"),
}


def collect_parameter_values(parameters, parameter_name):
    """
    Return the non-empty, de-duplicated values supplied for one parameter.

    Accepts a QueryDict, where a parameter may legitimately repeat, or a plain
    dict, so querysets can be tested without constructing a request.
    """
    if hasattr(parameters, "getlist"):
        raw_values = parameters.getlist(parameter_name)
    else:
        raw_value = parameters.get(parameter_name)
        raw_values = raw_value if isinstance(raw_value, list) else [raw_value]

    collected = []
    for raw_value in raw_values:
        cleaned = (raw_value or "").strip()
        if cleaned and cleaned not in collected:
            collected.append(cleaned)
    return collected
