#!/usr/bin/env bash
DEBUG=${DEBUG-}
VERBOSE=
SETTED=
if [[ -n $DEBUG ]];then
    VERBOSE="v"
    SETTED="x"
fi
set -e$SETTED
chown -Rf$VERBOSE $APP_USER .
if [ "x$@" = "x" ];then
    set -- python app.py
fi
if [ "x$(whoami)" = "xroot" ];then
    exec gosu $APP_USER "$@"
else
    exec "$@"
fi
# vim:set et sts=4 ts=4 tw=80:
