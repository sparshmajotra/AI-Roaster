from __future__ import annotations

from rest_framework.throttling import UserRateThrottle


class RoastSubmitThrottle(UserRateThrottle):
    scope = "roast_submit"

    def allow_request(self, request, view):
        if getattr(view, "action", None) != "create":
            return True
        return super().allow_request(request, view)
