#!/usr/bin/env bash
cd $(dirname $(readlink -f $0))
docker-compose run --rm backup ./probe.py "$@"
# vim:set et sts=4 ts=4 tw=80:
