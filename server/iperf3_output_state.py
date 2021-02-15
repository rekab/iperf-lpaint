import re
import transitions


class InvalidDataUpdateException(Exception):
    pass


class UnknownLineException(Exception):
    def __init__(self, model, line):
        self.model = model
        self.line = line
        super().__init__(f'state={model.state} but unknown line: {line}')


class IperfOutputStateModel(object):
    def __init__(self,
            bitrate_subscriber=None,
            jitter_subscriber=None,
            bitrate_summary_subscriber=None,
            listening_subscriber=None):
        self.bitrate_subscriber = bitrate_subscriber
        self.bitrate_summary_subscriber = bitrate_summary_subscriber
        self.listening_subscriber = listening_subscriber
        self.jitter_subscriber = jitter_subscriber

        self.cur_match = None

    def receive_data(self):
        print('got data: ', self.cur_match.groups())
        if self.bitrate_subscriber is not None:
            self.bitrate_subscriber(
                    float(self.cur_match.group('bitrate')),
                    self.cur_match.group('bitrate_unit'))
        if self.jitter_subscriber is not None:
            self.jitter_subscriber(
                    float(self.cur_match.group('jitter')))

    def receive_summary(self):
        print('got data: summary', self.cur_match.groups())
        if self.bitrate_summary_subscriber is not None:
            self.bitrate_summary_subscriber(
                    float(self.cur_match.group('bitrate')),
                    self.cur_match.group('bitrate_unit'))

    def listening(self):
        print('listening')
        if self.listening_subscriber is not None:
            self.listening_subscriber()


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
        {'trigger': 'divider', 'source': 'awaiting_connection1', 'dest': 'awaiting_connection2', 'after': 'listening'},
        {'trigger': 'divider', 'source': 'starting', 'dest': 'starting'},

        # connection and await data
        {'trigger': 'accepted_connection', 'source': 'awaiting_connection2', 'dest': 'accepted_connection1'},
        {'trigger': 'connection_info', 'source': 'accepted_connection1', 'dest': 'accepted_connection2'},
        {'trigger': 'header', 'source': 'accepted_connection2', 'dest': 'data'},
        # immediate disconnect: summary
        {'trigger': 'summary_divider', 'source': 'accepted_connection1', 'dest': 'summary'},

        # this is the money trigger
        {'trigger': 'data', 'source': 'data', 'dest': 'data', 'after': 'receive_data'},

        # end
        {'trigger': 'summary_divider', 'source': 'accepted_connection2', 'dest': 'summary'},
        {'trigger': 'summary_divider', 'source': 'awaiting_data', 'dest': 'summary'},
        {'trigger': 'summary_divider', 'source': 'data', 'dest': 'summary'},
        {'trigger': 'header', 'source': 'summary', 'dest': 'summary'},
        {'trigger': 'data', 'source': 'summary', 'dest': 'summary', 'after': 'receive_summary'},
        {'trigger': 'divider', 'source': 'summary', 'dest': 'starting'},
        # failures
        {'trigger': 'client_closed', 'source': 'accepted_connection1', 'dest': 'not_started'},
        {'trigger': 'client_closed', 'source': 'accepted_connection2', 'dest': 'not_started'},
        {'trigger': 'client_closed', 'source': 'summary', 'dest': 'not_started'},
    ]

    def __init__(self,
            bitrate_subscriber=None,
            jitter_subscriber=None,
            bitrate_summary_subscriber=None,
            listening_subscriber=None):
        self.model = IperfOutputStateModel(
            bitrate_subscriber=bitrate_subscriber,
            jitter_subscriber=jitter_subscriber,
            bitrate_summary_subscriber=bitrate_summary_subscriber,
            listening_subscriber=listening_subscriber)
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
                        r'(?P<transfer>\d+(\.\d+)?)\s+'
                        r'(?P<transfer_unit>[KMG])?Bytes\s+'
                        r'(?P<bitrate>\d+(\.\d+)?)\s+'
                        r'(?P<bitrate_unit>[KMG])bits/sec\s+'
                        r'(?P<jitter>\d+(\.\d+)?) ms\s+.*'), self.model.data),
            (re.compile(r'^(- )+.*'), self.model.summary_divider),
            (re.compile(r'^iperf3: the client'), self.model.client_closed),
            # this might need more investigation
            (re.compile(r'^WARNING:  Size of data read'), self.model.client_closed),
        ]

    def receive_line(self, line):
        self.cur_line = line
        for trigger in self.pattern_triggers:
            self.model.cur_match = trigger[0].match(self.cur_line)
            if self.model.cur_match:
                return trigger[1]()
        raise UnknownLineException(self.model, line)
