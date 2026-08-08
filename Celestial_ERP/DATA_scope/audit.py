from __future__ import annotations

from django.forms.models import model_to_dict

from Applet.audit import log_event


def snapshot(instance, fields: list[str] | tuple[str, ...] | None = None) -> dict[str, object]:
    if instance.pk is None:
        return {}
    data = model_to_dict(instance, fields=fields)
    return {key: str(value) for key, value in data.items()}


def changed_fields(before: dict[str, object], after: dict[str, object]) -> dict[str, tuple[object, object]]:
    changes = {}
    for key, old_value in before.items():
        new_value = after.get(key)
        if str(old_value) != str(new_value):
            changes[key] = (old_value, new_value)
    return changes


def object_type(instance) -> str:
    return f"{instance._meta.app_label}.{instance._meta.model_name}"


def log_manual_change(request, action: str, instance, before: dict[str, object] | None = None) -> None:
    label = str(instance)
    if before is None:
        log_event(
            request,
            action,
            "DATA_scope",
            f"{label}",
            object_type=object_type(instance),
            object_id=instance.pk,
            object_repr=label,
        )
        return
    after = snapshot(instance, fields=list(before.keys()))
    changes = changed_fields(before, after)
    if not changes:
        return
    change_text = ", ".join(f"{field}: {old} -> {new}" for field, (old, new) in changes.items())
    structured_changes = {
        field: {"old": str(old), "new": str(new)}
        for field, (old, new) in changes.items()
    }
    log_event(
        request,
        action,
        "DATA_scope",
        f"{label}; {change_text}",
        object_type=object_type(instance),
        object_id=instance.pk,
        object_repr=label,
        changes=structured_changes,
    )
