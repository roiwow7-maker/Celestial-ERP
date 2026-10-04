"""Controles comunes al portal, admin y API de una empresa."""
import hashlib
import json
import time
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from .audit import log_event
from .models import LoginThrottle


def login_buckets(request):
    try:
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        username = str(data.get("username", "")).strip().casefold()[:150]
    except (ValueError, AttributeError):
        username = ""
    # REMOTE_ADDR lo fija el servidor; nunca confiar en X-Forwarded-For del cliente.
    address = request.META.get("REMOTE_ADDR", "unknown")
    raw_keys = [(f"user:{username}", settings.ERP_LOGIN_ATTEMPTS), (f"ip:{address}", settings.ERP_LOGIN_ATTEMPTS * 6)]
    return [(hashlib.sha256(value.encode()).hexdigest(), limit) for value, limit in raw_keys]


def record_failure(buckets):
    now = timezone.now()
    LoginThrottle.objects.filter(expires_at__lte=now).delete()
    with transaction.atomic():
        for key, _ in buckets:
            row, _ = LoginThrottle.objects.select_for_update().get_or_create(
                key=key, defaults={"expires_at": now + timedelta(seconds=settings.ERP_LOGIN_WINDOW_SECONDS)},
            )
            if row.expires_at <= now:
                row.failures = 0
                row.expires_at = now + timedelta(seconds=settings.ERP_LOGIN_WINDOW_SECONDS)
            row.failures += 1
            row.save()


class SecurityBoundaryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = int(time.time())
        if request.user.is_authenticated:
            last_seen = request.session.get("erp_last_seen", now)
            if now - last_seen > settings.ERP_SESSION_IDLE_SECONDS:
                log_event(request, "session_expired", "security")
                logout(request)
            else:
                request.session["erp_last_seen"] = now

        is_login = request.method == "POST" and request.path in {"/api/v1/login/", "/login/", "/admin/login/"}
        buckets = login_buckets(request) if is_login else []
        if any(LoginThrottle.objects.filter(key=key, failures__gte=limit, expires_at__gt=timezone.now()).exists() for key, limit in buckets):
            result = JsonResponse({"error": "Demasiados intentos. Espera unos minutos antes de volver a ingresar."}, status=429)
            result["Retry-After"] = str(settings.ERP_LOGIN_WINDOW_SECONDS)
        else:
            result = self.get_response(request)
            if is_login and result.status_code != 403:
                if request.user.is_authenticated:
                    LoginThrottle.objects.filter(key=buckets[0][0]).delete()
                    request.session["erp_last_seen"] = now
                    log_event(request, "login_success", "security")
                else:
                    record_failure(buckets)
                    log_event(request, "login_failed", "security")
        result["X-ERP-Company"] = settings.ERP_COMPANY_ID
        if request.path.startswith("/api/") or request.user.is_authenticated:
            result["Cache-Control"] = "no-store, private"
        return result
