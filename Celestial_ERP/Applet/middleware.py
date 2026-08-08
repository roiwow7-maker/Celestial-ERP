from __future__ import annotations

from .services import run_auto_backup_if_due


class AutoBackupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        run_auto_backup_if_due(request)
        return response
