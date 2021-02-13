# Common functions and variables

set -e # exit on error
set -x # debug

log() {
  echo "$0: " $(date +'%Y-%m-%d %H:%M:%S'): "$@"
}

CLIENT_ADDR=10.5.5.2
SERVER_ADDR=10.5.5.1
CLIENT_RUN_DURATION_SECS=3600
BITRATE=0 # unlimited
LOOP_SLEEP_DURATION_SECS=5
LPAINT_OFF_FILE=$HOME/turn_off_lpaint

check_lpaint_off_file() {
  if [ -e $LPAINT_OFF_FILE ] ;
  then
    log "$LPAINT_OFF_FILE exists, so lpaint will not run."
    exit
  fi
}

loop_command() {
  while true ;
  do
    check_lpaint_off_file

    if $* ;
    then
      log "success"
    else
      log "return code: $?"
    fi

    log "sleeping $LOOP_SLEEP_DURATION_SECS seconds before retrying"
    sleep $LOOP_SLEEP_DURATION_SECS
  done
}
