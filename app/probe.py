#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os
import sys
import traceback
import argparse
import re
import subprocess

from dateutil import parser

from app import EXPORT_DIR


re_flags = re.I | re.U | re.X


class Check(object):
    def __init__(self, *a, **kw):
        self._program = "ovhbackup_lag_checks"
        self._author = "Makina Corpus (kiorky)"
        self._nick = self._program.replace("check_", "")
        self._ok = 0
        self._warning = 1
        self._critical = 2
        self._unknown = 3
        self.parser = None
        self.args = None
        self.options = None

    def compute_perfdata(self, force=True):
        if force or not self._perfdata:
            self._perfdata += "test=1"
        return self._perfdata

    def exit(self, code, msg="", perfdata=None):
        if perfdata:
            msg += "|{0}".format(perfdata.strip())
        if msg:
            print(msg)
        sys.exit(code)

    def critical(self, msg="", perfdata=None):
        msg = "{0} CRITICAL - {1}".format(self._nick, msg)
        self.exit(self._critical, msg=msg, perfdata=perfdata)

    def warning(self, msg="", perfdata=None):
        msg = "{0} WARNING - {1}".format(self._nick, msg)
        self.exit(self._warning, msg=msg, perfdata=perfdata)

    def unknown(self, msg="", perfdata=None):
        msg = "{0} UNKNOWN - {1}".format(self._nick, msg)
        self.exit(self._unknown, msg=msg, perfdata=perfdata)

    def ok(self, msg="", perfdata=None):
        msg = "{0} OK - {1}".format(self._nick, msg)
        self.exit(self._ok, msg=msg, perfdata=perfdata)

    def opt_parser(self):
        dlag = int(os.environ.get("OVHBACKUP_EXPIRY", 60*60*24))
        parser = self.parser = argparse.ArgumentParser(
            prog=self._program, description=("Check OVHBACKUP lag state")
        )
        parser.add_argument(
            "--lag-max",
            default=dlag,
            const=dlag,
            type=str,
            nargs="?",
            dest="lag",
            help="lag trigger",
        )
        parser.add_argument(
            "--warning",
            default=15 * dlag,
            const=15 * dlag,
            type=str,
            nargs="?",
            dest="wlag",
            help="warning lag trigger",
        )
        parser.add_argument(
            "--critical",
            default=30 * dlag,
            const=30 * dlag,
            type=float,
            nargs="?",
            dest="clag",
            help="critical lag trigger",
        )
        parser.add_argument("--export-dir", default=EXPORT_DIR)
        parser.add_argument(
            "--services", action="append", help="services to monitor"
        )
        self.args = vars(parser.parse_args())

    def run(self):
        method = self.unknown
        counters = {}
        lag = 0
        self.opt_parser()
        msg = ""
        if self.args["services"] is None:
            self.args["services"] = ["dns", "ipfo"]

        for service in self.args["services"]:
            lo = None
            ed = f"{self.args['export_dir']}/{service}"
            if not os.path.exists(ed):
                msg += f' -- data is missing for service {service}'
                method = self.critical
                continue
            ret = subprocess.check_output(
                f"""
                set -e
                cd {ed}
                cd {self.args['export_dir']}/{service}
                git log
                """,
                shell=True,
            ).decode('utf-8')
            for ln in ret.splitlines():
                if ln.startswith('Date:'):
                    sdt = re.sub("Date:\s+", '', ln)
                    lo = parser.parse(sdt)
                    break
            if lo is None:
                method = self.critical
                msg += f' -- no last run for {service} service'
                continue
            now = datetime.now(tz=lo.tzinfo)
            counters["{0}_last_ok".format(service)] = int(lo.timestamp())
            if method == self.unknown and lo:
                lag = int(now.timestamp() - lo.timestamp())
                nolag = not lag
                if lag:
                    if lag >= self.args["clag"]:
                        method = self.critical
                        msg = "data is very stale"
                    elif lag >= self.args["wlag"]:
                        method = self.warning
                        msg = "data is a bit stale"
                    else:
                        nolag = True
                if nolag:
                    method = self.ok
                    msg = "data is fresh"
        counters["lag"] = lag
        perfdata = ""
        for i, val in counters.items():
            perfdata += " {0}={1}".format(i, val)
        method(msg, perfdata=perfdata)


def main():
    try:
        check = Check()
        check.run()
    except (Exception,) as e:
        trace = traceback.format_exc()
        print("Unknown error UNKNOW - {0}".format(e))
        print(trace)
        sys.exit(3)


if __name__ == "__main__":
    main()
# vim:set et sts=4 ts=4 tw=80:
