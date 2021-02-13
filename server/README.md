Iperf light painter.

This is the server.

## disabling

touch ~/turn_off_lpaint

## crontab

```
@reboot /home/pi/code/iperf-lpaint/server/server.sh | multilog s1000000 n10 /home/pi/iperf-lpaint-logs/server_log/
```
