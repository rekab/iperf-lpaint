#!/bin/bash

log() {
  echo "$0: " $(date +'%Y-%m-%d %H:%M:%S'): "$@"
}


LPAINT_OFF_FILE=$HOME/turn_off_lpaint

check_lpaint_off_file() {
  if [ -e $LPAINT_OFF_FILE ] ;
  then
    log "$LPAINT_OFF_FILE exists, so lpaint will not run."
    exit
  fi
}

set -e # exit on error
set -x # debug

BIND_ADDR=10.5.5.2
SERVER_ADDR=10.5.5.1
RUN_DURATION_SECS=3600
BITRATE=0 # unlimited
SLEEP_DURATION_SECS=5

log "starting"

while true ;
do
  check_lpaint_off_file
  echo "launching iperf client..."
  if iperf3 -B $BIND_ADDR -c $SERVER_ADDR -u -t $RUN_DURATION_SECS -b $BITRATE;
  then
    log "success"
  else
    log "return code: $?"
  fi
  log "sleeping $SLEEP_DURATION_SECS seconds before retrying"
  sleep $SLEEP_DURATION_SECS
done
