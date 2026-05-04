from __future__ import absolute_import, unicode_literals
import os

try:
    from celery import Celery

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uctrade.settings')
    app = Celery('uctrade')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
except Exception:
    # Celery isn't available in this environment (e.g., developer machine without package).
    # Provide a minimal no-op fallback so imports don't fail and tasks can be executed synchronously.
    class _DummyCeleryApp:
        def task(self, *args, **kwargs):
            def _decorator(func):
                return func
            return _decorator

    app = _DummyCeleryApp()
