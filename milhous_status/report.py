# coding=utf-8
from __future__ import unicode_literals

import sys
import psutil
import requests
import json
import traceback


report_url = 'http://milhous.info:8010/state/host/state/'


def gen_report():
    vm = psutil.virtual_memory()
    cpu = psutil.cpu_percent(10, percpu=True)
    data = {
        "mem": {
            "total": vm.total,
            "used": vm.used,
        },
        "cpu": cpu,
    }
    return data


def do_request(report, hostname):
    try:
        print("reporting... %s" % report)
        r = requests.post(url=report_url, json={
            "data": {
                "host": hostname,
                "usages": json.dumps(report)
            }
        })
        print(r.status_code, r.content)
    except:
        print("Error while requesting.")
        traceback.print_exc()


if __name__ == '__main__':
    while True:
        do_request(gen_report(), sys.argv[1])
