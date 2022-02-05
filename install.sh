#!/usr/bin/env bash
set -x
cd $(dirname $(readlink -f $0))
docker-compose -f docker-compose.yml -f docker-compose-build.yml build
cp ovh-backup.service /etc/systemd/system
systemctl enable ovh-backup.service
systemctl start ovh-backup.service
# vim:set et sts=4 ts=4 tw=80:
