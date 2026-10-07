"""Resolve a playable URL for a ContentItem (Cloudflare R2 public URL or stored url)."""

from django.conf import settings


def resolve_playback_url(item):
    """
    Android ko yahi URL ExoPlayer / VideoView me dena hai.
    Priority: R2 public base + storage_key, else ContentItem.url
    """
    key = (getattr(item, "storage_key", None) or "").strip().lstrip("/")
    base = (getattr(settings, "R2_PUBLIC_BASE_URL", None) or "").rstrip("/")
    if key and base:
        return f"{base}/{key}"
    return item.url or ""


def mime_type_for(item):
    if item.content_type == "VIDEO":
        return "video/mp4"
    if item.content_type == "PDF":
        return "application/pdf"
    return "application/octet-stream"
