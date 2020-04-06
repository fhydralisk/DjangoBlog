# coding=utf-8
from __future__ import unicode_literals

import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from base.util.redis import get_redis
from base.util.sms.sms import sms_manager, sms_choice
from .models import MilhousHost


logger = get_task_logger(__name__)


@shared_task
def report_host_state():
    r = get_redis()
    state_changed = []
    logger.debug("Beat for host state detect")
    for host in MilhousHost.objects.all():
        k = host.redis_hb_key + '_isalive'
        is_alive_before = int(r.get(k) or 0)
        is_alive_now = 1 if host.is_alive else 0
        if is_alive_before ^ is_alive_now:
            logger.info('Host %s state change from %d to %d' % (host.name, is_alive_before, is_alive_now))
            state_changed.append(host)
        r.set(k, is_alive_now, ex=300)

    for host in state_changed:  # FIXME
        sms_manager[sms_choice.HOST_STATE].send_sms('18513958704', {
            'server_type': host.name,
            'date_start': datetime.datetime.now().strftime('%m-%d %H:%M'),
            'date_end': datetime.datetime.now().strftime('%m-%d %H:%M'),
            'count': 1,
        })
