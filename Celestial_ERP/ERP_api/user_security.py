from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from Applet.audit import log_event
from Applet.services import ROLE_NAMES


class UserAccessForm(forms.Form):
    username = forms.RegexField(regex=r"^[\w.@+-]+$", max_length=150, required=False)
    password = forms.CharField(required=False, max_length=256)
    first_name = forms.CharField(required=False, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)
    email = forms.EmailField(required=False)
    roles = forms.MultipleChoiceField(choices=[(name, name) for name in ROLE_NAMES], required=False)


def save_user(request, data, user_id=None):
    """Validar antes de escribir; cambios y auditoría pertenecen a una sola empresa."""
    User = get_user_model()
    creating = user_id is None
    permission = "auth.add_user" if creating else "auth.change_user"
    if not request.user.has_perm(permission):
        raise PermissionDenied
    form = UserAccessForm(data)
    if not form.is_valid():
        return None, form.errors.get_json_data()
    values = form.cleaned_data
    for field in ("is_active", "is_staff"):
        if field in data and type(data[field]) is not bool:
            return None, {field: ["Debe ser verdadero o falso."]}
    with transaction.atomic():
        # Orden fijo: impide que dos administradores eliminen simultáneamente el último acceso.
        locked = list(User.objects.select_for_update().order_by("pk"))
        user = User() if creating else next((row for row in locked if row.pk == user_id), None)
        if user is None:
            from django.http import Http404
            raise Http404
        if not creating and user.is_superuser and not request.user.is_superuser:
            raise PermissionDenied
        if creating:
            if not values["username"] or not values["password"]:
                return None, {"username": ["Usuario y contraseña son obligatorios."]}
            if User.objects.filter(username=values["username"]).exists():
                return None, {"username": ["El usuario ya existe."]}
            user.username = values["username"]
        old_roles = list(user.groups.values_list("name", flat=True)) if not creating else []
        for field in ("first_name", "last_name", "email", "is_active", "is_staff"):
            if field in data:
                setattr(user, field, values[field] if field in values else data[field])
        roles = values["roles"] if "roles" in data else old_roles
        if not creating and user.pk == request.user.pk and not user.is_active:
            return None, {"is_active": ["No puedes desactivar tu propia cuenta."]}
        if not creating and not user.is_superuser and "Administrador" in old_roles and (not user.is_active or "Administrador" not in roles):
            others = User.objects.filter(is_active=True).exclude(pk=user.pk)
            if not (others.filter(is_superuser=True).exists() or others.filter(groups__name="Administrador").exists()):
                return None, {"roles": ["Debe quedar al menos un administrador activo."]}
        if values["password"]:
            try:
                validate_password(values["password"], user)
            except ValidationError as exc:
                return None, {"password": exc.messages}
            user.set_password(values["password"])
        user.save()
        if creating or "roles" in data:
            user.groups.set(Group.objects.filter(name__in=roles))
        log_event(request, "user_created" if creating else "user_updated", "security", object_type="User", object_id=user.pk,
                  changes={"roles_before": old_roles, "roles_after": roles, "active": user.is_active, "password_changed": bool(values["password"])})
    return user, None
