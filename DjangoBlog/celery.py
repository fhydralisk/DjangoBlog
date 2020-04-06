from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from datetime import timedelta

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoBlog.settings')

app = Celery('DjangoBlog')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.update(
    CELERYBEAT_SCHEDULE={
        'report-host-state': {
            'task': 'milhous_status.tasks.report_host_state',
            'schedule': timedelta(seconds=30),
        }
    }
)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
