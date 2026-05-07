from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.roasts.models import RoastPost

User = get_user_model()

SYSTEM_PROMPT = """You are a witty internet comedian generating funny but non-hateful roasts.
Write the roast as 5 to 6 short lines separated by newline characters.
Be clever, meme-like, specific, and punchy.
For Brutal Roast, be savage, darker, and more cutting, but do not use hate speech, racist content, slurs, threats, sexual harassment, or attacks on protected traits.
Return only valid JSON with keys: roast, rating, vibe_tags, aura, improvement_suggestions."""


def upload_media_to_cloudinary(media_file) -> str:
    if not all(
        [
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        ]
    ):
        return ""

    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    result = cloudinary.uploader.upload(
        media_file,
        folder="roastly/submissions",
        resource_type="image",
        transformation=[
            {"width": 1400, "height": 1400, "crop": "limit"},
            {"quality": "auto:good"},
            {"fetch_format": "auto"},
        ],
    )
    return result.get("secure_url", "")


def moderate_submission(post: RoastPost) -> dict[str, Any]:
    if not settings.OPENAI_API_KEY:
        return {"flagged": False, "provider": "mock", "categories": {}}

    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    moderation_input = post.text_content or f"{post.get_category_display()} image submission for a roast platform."
    response = client.moderations.create(
        model=settings.OPENAI_MODERATION_MODEL,
        input=moderation_input[:4000],
    )
    result = response.results[0]
    categories = result.categories.model_dump() if hasattr(result.categories, "model_dump") else dict(result.categories)
    return {
        "flagged": bool(result.flagged),
        "provider": "openai",
        "categories": categories,
    }


def generate_ai_roast(post: RoastPost) -> dict[str, Any]:
    if not settings.OPENAI_API_KEY:
        return build_mock_roast(post)

    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    user_prompt = build_user_prompt(post)
    content: list[dict[str, Any]] = [{"type": "text", "text": user_prompt}]
    if post.media_url:
        content.append({"type": "image_url", "image_url": {"url": post.media_url}})

    response = client.chat.completions.create(
        model=settings.OPENAI_ROAST_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        temperature=0.85,
        max_tokens=500,
    )
    raw = response.choices[0].message.content or "{}"
    return normalize_ai_payload(json.loads(raw), post)


def build_user_prompt(post: RoastPost) -> str:
    return "\n".join(
        [
            f"Category: {post.get_category_display()}",
            f"Roast style: {post.get_roast_style_display()}",
            f"Visibility: {post.visibility}",
            f"Text content: {post.text_content[:2500] or 'Image-only submission'}",
            "Roast format: 5 to 6 short lines separated with newline characters.",
            "Make each line a separate joke or escalation.",
            "Keep it funny, memorable, and safe enough for a public social feed.",
        ]
    )


def build_mock_roast(post: RoastPost) -> dict[str, Any]:
    category = post.get_category_display().replace("Roast My ", "").lower()
    is_brutal = post.roast_style == RoastPost.RoastStyle.BRUTAL
    if is_brutal:
        roast = "\n".join(
            [
                f"This {category} walks in like it has a villain monologue and leaves like a deleted scene.",
                "The confidence is loud, but the execution is whispering for legal protection.",
                "It is giving main character energy from a movie nobody renewed for season two.",
                "Even the algorithm looked at this and asked if you had a backup personality.",
                "There is potential here, but right now it is wearing a disguise and missing rent.",
                "Fix one bold detail and this could be dangerous instead of just emotionally noisy.",
            ]
        )
        tips = [
            "Keep one strong focal point and remove the accidental chaos.",
            "Make the first impression sharper before asking the internet for mercy.",
        ]
        aura = "High Confidence, Low Alibi"
        tags = ["brutal mode", "main character debt", "almost dangerous", "needs editing"]
    else:
        roast = "\n".join(
            [
                f"This {category} has main-character ambition and group-chat audit risk.",
                "It is not failing, but it is absolutely asking the timeline for extra credit.",
                "The vibe wants to be iconic, then remembers it has errands.",
                "There is a good idea in here, currently hiding behind three questionable choices.",
                "Honestly, the potential is real, which makes the mess more personally disrespectful.",
                "Clean up the loudest detail and this could stop apologizing for itself.",
            ]
        )
        tips = [
            "Add one sharper focal point so the roast has less room to wander.",
            "Keep the best detail and remove anything that feels accidental.",
        ]
        aura = "Confident Work In Progress"
        tags = ["almost iconic", "algorithm friendly", "mild chaos", "reply bait"]

    return {
        "roast": roast,
        "rating": 6.4 if is_brutal else 7.6,
        "vibe_tags": tags,
        "aura": aura,
        "improvement_suggestions": tips,
    }


def normalize_ai_payload(payload: dict[str, Any], post: RoastPost) -> dict[str, Any]:
    fallback = build_mock_roast(post)
    rating = payload.get("rating", fallback["rating"])
    try:
        rating = max(0, min(10, float(rating)))
    except (TypeError, ValueError):
        rating = fallback["rating"]

    vibe_tags = payload.get("vibe_tags") or fallback["vibe_tags"]
    tips = payload.get("improvement_suggestions") or fallback["improvement_suggestions"]
    if not isinstance(vibe_tags, list):
        vibe_tags = fallback["vibe_tags"]
    if not isinstance(tips, list):
        tips = fallback["improvement_suggestions"]

    return {
        "roast": str(payload.get("roast") or fallback["roast"])[:1400],
        "rating": Decimal(str(round(rating, 1))),
        "vibe_tags": [str(tag)[:40] for tag in vibe_tags[:5]],
        "aura": str(payload.get("aura") or fallback["aura"])[:120],
        "improvement_suggestions": [str(tip)[:180] for tip in tips[:5]],
    }


def apply_roast_result(post: RoastPost, payload: dict[str, Any]) -> RoastPost:
    normalized = normalize_ai_payload(payload, post)
    post.ai_roast = normalized["roast"]
    post.ai_score = normalized["rating"]
    post.vibe_tags = normalized["vibe_tags"]
    post.aura = normalized["aura"]
    post.improvement_tips = normalized["improvement_suggestions"]
    post.status = RoastPost.Status.READY
    update_heat_score(post, save=False)
    post.save(
        update_fields=[
            "ai_roast",
            "ai_score",
            "vibe_tags",
            "aura",
            "improvement_tips",
            "status",
            "heat_score",
            "updated_at",
        ]
    )
    return post


def update_heat_score(post: RoastPost, save: bool = True) -> None:
    age_hours = max((timezone.now() - post.created_at).total_seconds() / 3600, 1)
    engagement = (post.reaction_count * 2.5) + (post.comment_count * 4) + (post.bookmark_count * 3) + post.share_count
    score_boost = float(post.ai_score or 0) * 8
    post.heat_score = round((engagement + score_boost) / (age_hours**0.35), 2)
    if save:
        post.save(update_fields=["heat_score", "updated_at"])


def award_xp(user, amount: int) -> None:
    fresh_user = User.objects.only("xp").get(pk=user.pk)
    xp = fresh_user.xp + amount
    User.objects.filter(pk=user.pk).update(xp=xp, level=1 + (xp // 1000))
