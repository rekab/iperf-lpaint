import pyswitch
import re
import transitions
"""
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37165
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-0.50   sec  63.6 KBytes  1042 Kbits/sec  0.598 ms  0/45 (0%)
[  5]   0.50-1.00   sec  63.6 KBytes  1043 Kbits/sec  0.194 ms  0/45 (0%)
[  5]   1.00-1.50   sec  63.6 KBytes  1043 Kbits/sec  0.154 ms  0/45 (0%)
[  5]   1.50-2.00   sec  65.0 KBytes  1066 Kbits/sec  0.340 ms  0/46 (0%)
[  5]   2.00-2.50   sec  63.6 KBytes  1043 Kbits/sec  0.164 ms  0/45 (0%)
[  5]   2.50-3.00   sec  63.6 KBytes  1043 Kbits/sec  0.369 ms  0/45 (0%)
[  5]   3.00-3.50   sec  63.6 KBytes  1043 Kbits/sec  0.101 ms  0/45 (0%)
[  5]   3.50-4.00   sec  62.2 KBytes  1019 Kbits/sec  0.640 ms  2/46 (4.3%)
[  5]   4.00-4.50   sec  63.6 KBytes  1043 Kbits/sec  0.603 ms  0/45 (0%)
[  5]   4.50-5.00   sec  62.2 KBytes  1019 Kbits/sec  0.173 ms  1/45 (2.2%)
[  5]   5.00-5.50   sec  63.6 KBytes  1043 Kbits/sec  0.115 ms  0/45 (0%)
[  5]   5.50-6.00   sec  63.6 KBytes  1043 Kbits/sec  0.283 ms  1/46 (2.2%)
[  5]   6.00-6.50   sec  63.6 KBytes  1043 Kbits/sec  0.050 ms  0/45 (0%)
[  5]   6.50-7.00   sec  60.8 KBytes   996 Kbits/sec  0.533 ms  2/45 (4.4%)
[  5]   7.00-7.50   sec  63.6 KBytes  1043 Kbits/sec  0.133 ms  0/45 (0%)
[  5]   7.50-8.00   sec  65.0 KBytes  1066 Kbits/sec  0.171 ms  0/46 (0%)
[  5]   8.00-8.50   sec  63.6 KBytes  1043 Kbits/sec  0.207 ms  0/45 (0%)
[  5]   8.50-9.00   sec  63.6 KBytes  1043 Kbits/sec  0.074 ms  0/45 (0%)
[  5]   9.00-9.50   sec  65.0 KBytes  1066 Kbits/sec  0.067 ms  0/46 (0%)
[  5]   9.50-10.00  sec  63.6 KBytes  1043 Kbits/sec  0.188 ms  0/45 (0%)
[  5]  10.00-10.01  sec  1.41 KBytes  1081 Kbits/sec  0.226 ms  0/1 (0%)
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.01  sec  1.24 MBytes  1041 Kbits/sec  0.226 ms  6/906 (0.66%)  receiver
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
"""

class IperfOutputStateModel(object):
    pass


class IperfServerStateDriver(object):
    states = [
            'not_started',              # state 0 is the initial state
            'starting',
            'startup',
            'awaiting_connection',
            'accepted_connection',
            'main_header',
            'data',
            'data_end',
            'summary_header',
            'summary',
    ]

    def __init__(self,
            bitrate_subscriber=None,
            bitrate_summary_subscriber=None):
        self.bitrate_subscriber = bitrate_subscriber
        self.bitrate_summary_subscriber = bitrate_summary_subscriber
        self.cur_state = states[0]
        self.model = IperfOutputStateModel()
        self.machine = transitions.Machine(
                model=self.model, states=states, initial=states[0])
        self.machine.add_transition(
                trigger='on_start',
                source='not_started',
                dest='starting')

        self.patterns
        self.divider_pattern = re.compile(r'^-+$')
        self.header_pattern = re.compile(r'^\[\s*\d+]\s+Interval\+Transfer.*')
        self.server_listening_pattern = re.compile(r'^Server listening on \d+')
        self.accepted_connection_pattern = re.compile(r'^Accepted connection from.*')
        self.connection_info_pattern = re.compile(r'^\[\s*\d+]\s+local \d+\.\d+\.\d+\.\d+.*')
        self.data_pattern = re.compile(r'\[\s*\d+]\s+local \d+\.\d+\.\d+\.\d+.*')
        self.summary_divider_pattern = re.compile(r'^(- )+.*')
    

    def receive_line(self, line):
        """
        Receive a line of text. Accepts lines with newline characters.
        """
        self.cur_line = line

        if self.divider_pattern.match(line):
            return self.machine.on_divider()

        if self.header_pattern.match(line):
            return self.machine.on_header()

        if self.server_listening_pattern.match(line):
            return self.machine.on_server_listening()

        if self.accepted_connection_pattern.match(line):
            return self.machine.on_accepted_connection()

        if self.connection_info_pattern.match(line):
            return self.machine.on_connection_info()

        if self.data_pattern.match(line):
            return self.on_data()

        if self.summary_divider_pattern.match(line):
            return self.on_summary_header()

