import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uctrade.settings')
import django
django.setup()
from payments.urls import urlpatterns
import inspect
for pattern in urlpatterns:
    if getattr(pattern, 'callback', None):
        print('module', pattern.callback.__module__)
        print('qualname', pattern.callback.__qualname__)
        print(inspect.getsource(pattern.callback.view_class.post))
