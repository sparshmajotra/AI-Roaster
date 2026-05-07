from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from apps.moderation.models import ModerationAction
from apps.moderation.serializers import ModerationActionSerializer, ModerationQueueSerializer
from apps.roasts.models import Report, RoastPost
from apps.roasts.serializers import ReportSerializer, RoastPostSerializer


class ModerationQueueView(GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ModerationQueueSerializer

    def get(self, request):
        pending_posts = RoastPost.objects.filter(status__in=[RoastPost.Status.PENDING, RoastPost.Status.REJECTED]).select_related("user")[:50]
        reports = Report.objects.filter(is_resolved=False).select_related("reporter", "roast_post", "roast_post__user")[:50]
        return Response(
            {
                "pending_posts": RoastPostSerializer(pending_posts, many=True, context={"request": request}).data,
                "reported_posts": ReportSerializer(reports, many=True).data,
            }
        )


class ModerationActionViewSet(viewsets.ModelViewSet):
    queryset = ModerationAction.objects.select_related("target_user", "roast_post", "created_by")
    serializer_class = ModerationActionSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        action = serializer.save(created_by=self.request.user)
        post = action.roast_post
        if post and action.action == ModerationAction.Action.HIDE_POST:
            post.status = RoastPost.Status.REJECTED
            post.save(update_fields=["status", "updated_at"])
        if post and action.action == ModerationAction.Action.RESTORE:
            post.status = RoastPost.Status.READY
            post.save(update_fields=["status", "updated_at"])

    @action(detail=True, methods=["post"])
    def resolve_report(self, request, pk=None):
        action = self.get_object()
        if not action.roast_post_id:
            return Response({"detail": "Action is not tied to a roast post."}, status=status.HTTP_400_BAD_REQUEST)
        count = Report.objects.filter(roast_post=action.roast_post, is_resolved=False).update(is_resolved=True)
        return Response({"resolved_reports": count})
