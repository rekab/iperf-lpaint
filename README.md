# iperf-lpaint

It kinda works but isn't that interesting.

### Prior art

https://blog.jasonantman.com/2018/11/open-source-wifi-site-survey-tool/
http://www.digitalethereal.com/processingcode.html

### Hardware

Two Raspberry Pis running Raspian 10.10 (buster).

One runs the iPerf server, and is connected via GPIO to a 0.5m (73 pixel) Adafruit Dotstar.

The other runs the iPerf client.


### Client setup:

The client boots up, gets an IP address from the server via DHCP, then runs the
iPerf client.

```
sudo systemctl enable ssh
sudo systemctl start ssh
sudo dpkg-reconfigure tzdata
sudo apt-get install vim git tig etckeeper python3-venv python3-pip iperf3 daemontools
```

Add to /etc/wpa_supplicant/wpa_supplicant.conf:

```
country=US

network={
    ssid="lpaint"
    psk="<whatever>"
}
```


Run `ifconfig` or something to get the mac address of its wifi device so that the server

### Server (lpainter host) setup:


```
sudo systemctl enable ssh
sudo systemctl start ssh
sudo dpkg-reconfigure tzdata
sudo apt-get install vim git tig etckeeper python3-venv python3-pip iperf3 dnsmasq hostapd daemontools
```

https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

```
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
pip3 install aiohttp 
pip3 install -r requirements.txt
```

Turn off dhcp serving for eth0 which would be bad. Edit `/etc/dnsmasq.conf`, add:

```
interface=wlan0
dhcp-range=10.5.5.2,10.5.5.100,255.255.255.0,24h
domain=wlan
address=/lpaint-server.wlan/10.5.5.1
dhcp-host=your-client-pi-mac-address-here,10.5.5.2
```


Edit /etc/hosts and add the client ip for convenience.

```
127.0.1.1               lpaint-server
10.5.5.2                lpaint-client
```


Add to /etc/dhcpcd.conf:

```
# lpainting experiment: set wlan0 is a host ap
interface wlan0
  static ip_address=10.5.5.1/24
  nohook wpa_supplicant
```

turn on radios (this might not be necessary if country code set):
```
sudo rfkill unblock wlan
```


Setup hostapd, edit /etc/hostapd/hostapd.conf:
```
hostapd/hostapd.conf 
country_code=US
interface=wlan0
ssid=lpaint
hw_mode=g
channel=7
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=<whatever>
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

Run `ifconfig wlan0 up` and check that it worked.
