#!/bin/bash
source $(dirname $0)/../common.sh

log "starting"

loop_command iperf3 -B $CLIENT_ADDR -c $SERVER_ADDR -u -t $CLIENT_RUN_DURATION_SECS -b $BITRATE
