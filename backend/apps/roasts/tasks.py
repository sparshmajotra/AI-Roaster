from __future__ import annotations

from celery import shared_task

from apps.notifications.services import create_notification
from apps.roasts.models import RoastPost
from apps.roasts.services import apply_roast_result, award_xp, generate_ai_roast, moderate_submission


@shared_task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def generate_roast_for_post(self, post_id: int) -> dict:
    post = RoastPost.objects.select_related("user").get(pk=post_id)
    post.status = RoastPost.Status.PROCESSING
    post.save(update_fields=["status", "updated_at"])

    try:
        moderation = moderate_submission(post)
        post.moderation_status = moderation
        if moderation.get("flagged"):
            post.status = RoastPost.Status.REJECTED
            post.save(update_fields=["moderation_status", "status", "updated_at"])
            create_notification(
                user=post.user,
                type="moderation",
                reference_id=post.pk,
                message="Your roast request needs review before it can be posted.",
            )
            return {"status": post.status, "post_id": post.pk}

        post.save(update_fields=["moderation_status", "updated_at"])
        payload = generate_ai_roast(post)
        apply_roast_result(post, payload)
        award_xp(post.user, 35)
        create_notification(
            user=post.user,
            type="roast_complete",
            reference_id=post.pk,
            message="Your AI roast is ready.",
        )
        return {"status": post.status, "post_id": post.pk}
    except Exception as exc:
        post.status = RoastPost.Status.FAILED
        post.moderation_status = {**post.moderation_status, "error": str(exc)[:240]}
        post.save(update_fields=["status", "moderation_status", "updated_at"])
        raise
