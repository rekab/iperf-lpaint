#!/bin/bash

SERVER_SRC_DIR=$(dirname $0)

source $SERVER_SRC_DIR/../common.sh
source $SERVER_SRC_DIR/venv/bin/activate

log "starting"

loop_command python3 $SERVER_SRC_DIR/iperf_server_monitor.py
