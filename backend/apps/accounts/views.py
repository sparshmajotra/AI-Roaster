from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Follow
from apps.accounts.serializers import ProfileUpdateSerializer, PublicUserSerializer, RegisterSerializer, UserSerializer
from apps.notifications.services import create_notification

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    search_fields = ["username", "bio"]
    ordering_fields = ["date_joined", "xp", "followers_count"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        if self.action == "create":
            return RegisterSerializer
        if self.action == "me" and self.request.method == "PATCH":
            return ProfileUpdateSerializer
        if self.action in {"list", "retrieve"}:
            return PublicUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        if self.action in {"me", "follow", "unfollow"}:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == "PATCH":
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def demo_token(self, request):
        if not (settings.DEBUG or settings.ROASTLY_ENABLE_DEMO_LOGIN):
            return Response({"detail": "Demo login is disabled."}, status=status.HTTP_403_FORBIDDEN)

        user, _ = User.objects.get_or_create(
            username="demo_roaster",
            defaults={
                "email": "demo@roastly.local",
                "bio": "Local demo account for testing Roastly.",
                "xp": 8400,
                "level": 9,
            },
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        target = self.get_object()
        if target == request.user:
            return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if created:
            User.objects.filter(pk=request.user.pk).update(following_count=F("following_count") + 1)
            User.objects.filter(pk=target.pk).update(followers_count=F("followers_count") + 1)
            create_notification(
                user=target,
                actor=request.user,
                type="follow",
                reference_id=request.user.pk,
                message=f"{request.user.username} followed you.",
            )
        return Response({"following": True, "created": created})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        target = self.get_object()
        deleted, _ = Follow.objects.filter(follower=request.user, following=target).delete()
        if deleted:
            User.objects.filter(pk=request.user.pk, following_count__gt=0).update(following_count=F("following_count") - 1)
            User.objects.filter(pk=target.pk, followers_count__gt=0).update(followers_count=F("followers_count") - 1)
        return Response({"following": False, "deleted": bool(deleted)})
