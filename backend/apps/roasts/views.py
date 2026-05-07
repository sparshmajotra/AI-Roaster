from __future__ import annotations

from django.conf import settings
from django.db.models import F, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Follow
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from apps.roasts.filters import RoastPostFilter
from apps.roasts.models import Bookmark, Comment, CommentVote, Reaction, Report, RoastPost
from apps.roasts.serializers import CommentSerializer, ReportSerializer, RoastPostSerializer
from apps.roasts.services import update_heat_score, upload_media_to_cloudinary
from apps.roasts.tasks import generate_roast_for_post
from common.permissions import IsOwnerOrReadOnly


class RoastPostViewSet(viewsets.ModelViewSet):
    serializer_class = RoastPostSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filterset_class = RoastPostFilter
    search_fields = ["text_content", "ai_roast", "aura"]
    ordering_fields = ["created_at", "heat_score", "ai_score", "reaction_count", "comment_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = RoastPost.objects.select_related("user")
        user = self.request.user

        if self.action in {"list", "trending", "recent"}:
            return qs.filter(status=RoastPost.Status.READY, visibility=RoastPost.Visibility.PUBLIC)

        if self.action == "following":
            if not user.is_authenticated:
                return qs.none()
            following_ids = Follow.objects.filter(follower=user).values("following_id")
            return qs.filter(
                user_id__in=following_ids,
                status=RoastPost.Status.READY,
                visibility__in=[RoastPost.Visibility.PUBLIC, RoastPost.Visibility.FOLLOWERS],
            )

        if not user.is_authenticated:
            return qs.filter(status=RoastPost.Status.READY, visibility=RoastPost.Visibility.PUBLIC)

        return qs.filter(
            Q(user=user)
            | Q(status=RoastPost.Status.READY, visibility=RoastPost.Visibility.PUBLIC)
            | Q(
                status=RoastPost.Status.READY,
                visibility=RoastPost.Visibility.FOLLOWERS,
                user__follower_edges__follower=user,
            )
        ).distinct()

    def get_permissions(self):
        if self.action in {"create", "react", "bookmark", "share", "report", "following"}:
            return [IsAuthenticated()]
        if self.action == "comments" and self.request.method == "POST":
            return [IsAuthenticated()]
        if self.action in {"update", "partial_update", "destroy"}:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user=request.user)

        if post.media and not post.media_url:
            post.media_url = upload_media_to_cloudinary(post.media) or request.build_absolute_uri(post.media.url)
            post.save(update_fields=["media_url", "updated_at"])

        generate_roast_for_post.delay(post.pk)
        post.refresh_from_db()
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(post).data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["get"])
    def trending(self, request):
        queryset = self.filter_queryset(self.get_queryset().order_by("-heat_score", "-created_at"))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        queryset = self.filter_queryset(self.get_queryset().order_by("-created_at"))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def following(self, request):
        queryset = self.filter_queryset(self.get_queryset().order_by("-created_at"))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == "GET":
            queryset = post.comments.filter(is_hidden=False).select_related("user")
            page = self.paginate_queryset(queryset)
            serializer = CommentSerializer(page or queryset, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)

        serializer = CommentSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user=request.user, roast_post=post)
        RoastPost.objects.filter(pk=post.pk).update(comment_count=F("comment_count") + 1)
        post.refresh_from_db()
        update_heat_score(post)
        if post.user_id != request.user.id:
            create_notification(
                user=post.user,
                actor=request.user,
                type=Notification.Type.COMMENT,
                reference_id=post.pk,
                message=f"{request.user.username} commented on your roast.",
            )
        return Response(CommentSerializer(comment, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def react(self, request, pk=None):
        post = self.get_object()
        emoji_type = request.data.get("emoji_type", Reaction.EmojiType.FIRE)

        if request.method == "DELETE":
            deleted, _ = Reaction.objects.filter(user=request.user, roast_post=post, emoji_type=emoji_type).delete()
            if deleted:
                RoastPost.objects.filter(pk=post.pk, reaction_count__gt=0).update(reaction_count=F("reaction_count") - 1)
            post.refresh_from_db()
            update_heat_score(post)
            return Response({"reacted": False, "emoji_type": emoji_type})

        reaction, created = Reaction.objects.get_or_create(user=request.user, roast_post=post, emoji_type=emoji_type)
        if created:
            RoastPost.objects.filter(pk=post.pk).update(reaction_count=F("reaction_count") + 1)
            if post.user_id != request.user.id:
                create_notification(
                    user=post.user,
                    actor=request.user,
                    type=Notification.Type.LIKE,
                    reference_id=post.pk,
                    message=f"{request.user.username} reacted to your roast.",
                )
        post.refresh_from_db()
        update_heat_score(post)
        return Response({"reacted": True, "emoji_type": reaction.emoji_type, "created": created})

    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        post = self.get_object()
        if request.method == "DELETE":
            deleted, _ = Bookmark.objects.filter(user=request.user, roast_post=post).delete()
            if deleted:
                RoastPost.objects.filter(pk=post.pk, bookmark_count__gt=0).update(bookmark_count=F("bookmark_count") - 1)
            return Response({"bookmarked": False})

        _, created = Bookmark.objects.get_or_create(user=request.user, roast_post=post)
        if created:
            RoastPost.objects.filter(pk=post.pk).update(bookmark_count=F("bookmark_count") + 1)
        post.refresh_from_db()
        update_heat_score(post)
        return Response({"bookmarked": True, "created": created})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def share(self, request, pk=None):
        post = self.get_object()
        RoastPost.objects.filter(pk=post.pk).update(share_count=F("share_count") + 1)
        post.refresh_from_db()
        update_heat_score(post)
        return Response({"share_url": f"{settings.ROASTLY_FRONTEND_URL}/roasts/{post.pk}", "share_count": post.share_count})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def report(self, request, pk=None):
        post = self.get_object()
        serializer = ReportSerializer(data={**request.data, "roast_post": post.pk})
        serializer.is_valid(raise_exception=True)
        report = serializer.save(reporter=request.user, roast_post=post)
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(is_hidden=False).select_related("user", "roast_post")

    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        comment = self.get_object()
        value = int(request.data.get("value", 1))
        value = CommentVote.Vote.UP if value >= 0 else CommentVote.Vote.DOWN
        CommentVote.objects.update_or_create(user=request.user, comment=comment, defaults={"value": value})
        comment.upvotes = comment.votes.filter(value=CommentVote.Vote.UP).count()
        comment.downvotes = comment.votes.filter(value=CommentVote.Vote.DOWN).count()
        comment.save(update_fields=["upvotes", "downvotes"])
        return Response(CommentSerializer(comment, context=self.get_serializer_context()).data)
