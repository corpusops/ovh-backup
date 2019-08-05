#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime
import ovh as _ovh
import traceback
import json
import requests
from datetime import datetime, timedelta
import logging
import re
import time
from raven import Client
from collections import OrderedDict
import subprocess


LOG_FORMAT = "%(asctime)s  [%(levelname)-5.5s]  %(message)s"
log = logging.getLogger(__name__)
re_flags = re.U | re.M
SENTRY_URL = os.environ.get("SENTRY_URL", None)
LOOP_INTERVAL = int(os.environ.get("LOOP_INTERVAL", 60 * 60 * 24))
EXPORTERS = OrderedDict()
_default = object()
EXPORT_DIR = os.environ.get("OVH_BACKUP_EXPORT_DIR", "/app/backup")


def splitstrip(v, splitter=_default):
    if v:
        if splitter is _default:
            v = [a.strip() for a in v.split()]
        else:
            v = [a.strip() for a in v.split(splitter)]
    else:
        v = []
    return v


def report_err(sentry_url=SENTRY_URL, trace=None):
    if sentry_url:
        client = Client(sentry_url)
        client.captureException()
    elif trace:
        log.error(trace)


class Exporter(object):
    def __init__(self, loop):
        self.loop = loop
        self.ovh = loop.ovh
        self.export_dir = os.path.join(
            EXPORT_DIR, self.__class__.__name__.lower()
        )

    def is_exportable(self):
        ret = False
        id_ = self.__class__.__name__.upper()
        if os.environ.get("OVH_BACKUP_EXPORT_{0}".format(id_)).strip():
            ret = True
        eservices = [
            a.upper()
            for a in splitstrip(
                os.environ.get("OVH_BACKUP_EXPORT_SERVICES", "")
            )
        ]
        if id_ in eservices:
            ret = True
        return ret

    def run_export(self):
        raise NotImplementedError()

    def export(self):
        if self.is_exportable():
            log.info(
                "Export {0} to {1}".format(
                    self.__class__.__name__, self.export_dir
                )
            )
            if not os.path.exists(self.export_dir):
                os.makedirs(self.export_dir)
            ret = self.run_export()
            gitd = os.path.join(self.export_dir, '.git')
            if not os.path.exists(gitd):
                subprocess.check_call(f'''
                                      set -ex
                                      cd {self.export_dir}
                                      git init
                                      ''', shell=True)

            subprocess.check_call(f'''
                                  set -ex
                                  cd {self.export_dir}
                                  git config user.email ovh@backup
                                  git config user.name ovhbackup
                                  git add . -f
                                  git commit -am autocommit
                                  ''', shell=True)
            return ret


class DNS(Exporter):
    def run_export(self):
        ovh = self.ovh
        zones = ovh.get("/domain")
        for zoneName in sorted(zones):
            log.info(f"Exporting {zoneName}")
            try:
                ret = ovh.get(f"/domain/zone/{zoneName}/export")
                f = os.path.join(self.export_dir, f"{zoneName}.zone")
                with open(f, "w") as fic:
                    fic.write(ret)
            except _ovh.exceptions.ResourceNotFoundError:
                continue


def register_exporter(exporter):
    EXPORTERS[exporter.__name__.lower()] = exporter


class Loop(object):
    def __init__(self):
        """
        relies on
        OVH_ENDPOINT
        OVH_APPLICATION_KEY
        OVH_APPLICATION_SECRET
        OVH_CONSUMER_KEY
        """
        self.ovh = _ovh.Client()

    def run(self):
        for exporter in EXPORTERS:
            EXPORTERS[exporter](self).export()


def __call__(*a, **kw):
    logging.basicConfig(format=LOG_FORMAT)
    log.setLevel(logging.DEBUG)
    while True:
        try:
            Loop().run()
            log.debug(f"Sleeping  {LOOP_INTERVAL}s")
            time.sleep(LOOP_INTERVAL)
        except KeyboardInterrupt:
            raise
        except:  # noqa
           trace = traceback.format_exc()
           print(trace)
           if SENTRY_URL:
               report_err(SENTRY_URL, trace)


register_exporter(DNS)

if __name__ == "__main__":
    __call__()

# vim:set et sts=4 ts=4 tw=80:
