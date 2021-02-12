#!/bin/bash

set -e # exit on error
set -x # debug

CLIENT_LOG_DIR=~/iperf_lpaint/client_log

mkdir -p $CLIENT_LOG_DIR

STDOUT_LOG=$CLIENT_LOG_DIR/STDOUT
STDERR_LOG=$CLIENT_LOG_DIR/STDERR

# Open STDOUT as $LOG_FILE file for append
exec 1>>$STDOUT_LOG
exec 2>>$STDERR_LOG

echo starting
date

while true ;
do
  if iperf3 -B 10.5.5.2 -c 10.5.5.1 -u -t 3600 >> $CLIENT_LOG_DIR/STDOUT 2>> $CLIENT_LOG_DIR/STDERR ;
  then
    echo success
    date
  else
    echo "return code: $?"
    date
  fi
  echo "sleeping 5 seconds before retrying"
  sleep 5
done
