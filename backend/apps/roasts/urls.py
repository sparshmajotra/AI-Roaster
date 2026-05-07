from __future__ import annotations

from rest_framework.routers import DefaultRouter

from apps.roasts.views import CommentViewSet, RoastPostViewSet

router = DefaultRouter()
router.register("posts", RoastPostViewSet, basename="roast-post")
router.register("comments", CommentViewSet, basename="comment")

urlpatterns = router.urls
