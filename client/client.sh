#!/bin/bash

set -e # exit on error
set -x # debug

BIND_ADDR=10.5.5.2
SERVER_ADDR=10.5.5.1
RUN_DURATION_SECS=3600
BITRATE=0 # unlimited

log() {
  echo $(date +'%Y-%m-%d %H:%M:%S'): "$@"
}

log "starting"

while true ;
do
  echo "launching iperf client..."
  if iperf3 -B $BIND_ADDR -c $SERVER_ADDR -u -t $RUN_DURATION_SECS -b $BITRATE;
  then
    log "success"
  else
    log "return code: $?"
  fi
  log "sleeping 5 seconds before retrying"
  sleep 5
done
