from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.moderation.views import ModerationActionViewSet, ModerationQueueView

router = DefaultRouter()
router.register("actions", ModerationActionViewSet, basename="moderation-action")

urlpatterns = [
    path("queue/", ModerationQueueView.as_view(), name="moderation-queue"),
    *router.urls,
]
