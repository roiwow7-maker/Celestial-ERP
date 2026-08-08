from __future__ import annotations

from .models import AuditLog


def log_event(
    request,
    action: str,
    module: str,
    description: str = "",
    *,
    object_type: str = "",
    object_id: str | int = "",
    object_repr: str = "",
    changes: dict | None = None,
) -> None:
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        user = None
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            module=module,
            description=description,
            object_type=object_type,
            object_id=str(object_id or ""),
            object_repr=object_repr,
            changes=changes or {},
        )
    except Exception:
        # La auditoria no debe botar una pantalla operativa.
        return
