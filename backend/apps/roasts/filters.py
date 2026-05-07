from __future__ import annotations

import django_filters

from apps.roasts.models import RoastPost


class RoastPostFilter(django_filters.FilterSet):
    min_score = django_filters.NumberFilter(field_name="ai_score", lookup_expr="gte")
    max_score = django_filters.NumberFilter(field_name="ai_score", lookup_expr="lte")

    class Meta:
        model = RoastPost
        fields = ["category", "roast_style", "status", "visibility", "is_anonymous", "min_score", "max_score"]
