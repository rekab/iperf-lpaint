Scripts to run the iperf client and the lpaint client control webserver at
startup.

## disabling

touch ~/turn_off_lpaint

## crontab

```
@reboot /home/pi/code/iperf-lpaint/client/client.sh | multilog s1000000 n10 /home/pi/iperf-lpaint-logs/client_log/
@reboot bash -c 'mkdir -p /home/pi/iperf-lpaint-logs ; cd /home/pi/iperf-lpaint-logs ; python3 -m http.server 2>&1 | multilog s1000000 n10 /home/pi/iperf-lpaint-logs/http_server_log/'
```
