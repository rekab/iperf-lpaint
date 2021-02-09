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

class InvalidDataUpdateException(Exception):
    pass


class UnknownLineException(Exception):
    def __init__(self, model, line):
        self.model = model
        self.line = line
        super().__init__('state={} but unknown line: {}'.format(model.state, line))


class IperfOutputStateModel(object):
    def __init__(self,
            bitrate_subscriber=None,
            bitrate_summary_subscriber=None):
        self.bitrate_subscriber = bitrate_subscriber
        self.bitrate_summary_subscriber = bitrate_summary_subscriber

        self.cur_match = None

    def receive_data(self):
        print('got data: ', self.cur_match.groups())
        if self.bitrate_subscriber is not None:
            self.bitrate_subscriber(float(self.cur_match.group('bitrate'))) 

    def receive_summary(self):
        print('got data: summary', self.cur_match.groups())
        if self.bitrate_summary_subscriber is not None:
            self.bitrate_summary_subscriber(float(self.cur_match.group('bitrate'))) 


class IperfServerStateDriver(object):
    states = [
        'not_started',              # state 0 is the initial state
        'starting',
        'awaiting_connection1',
        'awaiting_connection2',
        'accepted_connection1',
        'accepted_connection2',
        'data',
        'summary',
    ]
    transitions = [
        # startup and await connection
        {'trigger': 'divider', 'source': 'not_started', 'dest': 'starting'},
        {'trigger': 'server_listening', 'source': 'starting', 'dest': 'awaiting_connection1'},
        {'trigger': 'divider', 'source': 'awaiting_connection1', 'dest': 'awaiting_connection2'},

        # connection and await data
        {'trigger': 'accepted_connection', 'source': 'awaiting_connection2', 'dest': 'accepted_connection1'},
        {'trigger': 'connection_info', 'source': 'accepted_connection1', 'dest': 'accepted_connection2'},
        {'trigger': 'header', 'source': 'accepted_connection2', 'dest': 'data'},

        # this is the money trigger
        {'trigger': 'data', 'source': 'data', 'dest': 'data', 'after': 'receive_data'},

        # end
        {'trigger': 'summary_divider', 'source': 'accepted_connection2', 'dest': 'summary'},
        {'trigger': 'summary_divider', 'source': 'awaiting_data', 'dest': 'summary'},
        {'trigger': 'summary_divider', 'source': 'data', 'dest': 'summary'},
        {'trigger': 'header', 'source': 'summary', 'dest': 'summary'},
        {'trigger': 'data', 'source': 'summary', 'dest': 'summary', 'after': 'receive_summary'},
        {'trigger': 'divider', 'source': 'summary', 'dest': 'starting'},
    ]

    def __init__(self,
            bitrate_subscriber=None,
            bitrate_summary_subscriber=None):
        self.model = IperfOutputStateModel(
            bitrate_subscriber=bitrate_subscriber,
            bitrate_summary_subscriber=bitrate_summary_subscriber)
        self.machine = transitions.Machine(
                model=self.model,
                states=self.states,
                transitions=self.transitions,
                initial=self.states[0])

        # list of patterns
        self.pattern_triggers = [
            (re.compile(r'^-+$'), self.model.divider),
            (re.compile(r'^Server listening on \d+'), self.model.server_listening),
            (re.compile(r'^Accepted connection from.*'), self.model.accepted_connection),
            (re.compile(r'^\[\s*\d+\]\s+local \d+\.\d+\.\d+\.\d+.*'), self.model.connection_info),
            (re.compile(r'^\[\s*ID\]\s+Interval\s+Transfer.*'), self.model.header),
            (re.compile(r'\[\s*\d+\]\s+'
                        r'(?P<interval>\d+\.\d+-\d+\.\d+)\s+sec\s+'
                        r'(?P<transfer>\d+\.\d+)\s+'
                        r'(?P<transfer_unit>[KMG])Bytes\s+'
                        r'(?P<bitrate>\d+(\.\d+)?)\s+Kbits/sec.*'), self.model.data),
            (re.compile(r'^(- )+.*'), self.model.summary_divider),
        ]

    def receive_line(self, line):
        """
        Receive a line of text. Accepts lines with newline characters.
        """
        self.cur_line = line
        for trigger in self.pattern_triggers:
            self.model.cur_match = trigger[0].match(self.cur_line)
            if self.model.cur_match:
                return trigger[1]()
        raise UnknownLineException(self.model, line)
