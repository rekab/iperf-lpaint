import iperf3_output_state
import unittest
from unittest.mock import Mock
from unittest.mock import call


SIMPLE_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37165
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-0.50   sec  63.6 KBytes  1042 Kbits/sec  0.598 ms  0/45 (0%)
[  5]  10.00-10.01  sec  1.41 KBytes  1081 Kbits/sec  0.226 ms  0/1 (0%)
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.01  sec  1.24 MBytes  1041 Kbits/sec  0.226 ms  6/906 (0.66%)  receiver
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
"""

RECONNECTED_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37165
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-0.50   sec  63.6 KBytes  1042 Kbits/sec  0.598 ms  0/45 (0%)
[  5]  10.00-10.01  sec  1.41 KBytes  1081 Kbits/sec  0.226 ms  0/1 (0%)
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.01  sec  1.24 MBytes  1041 Kbits/sec  0.226 ms  6/906 (0.66%)  receiver
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37165
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-0.50   sec  63.6 KBytes  1234 Kbits/sec  0.598 ms  0/45 (0%)
[  5]  10.00-10.01  sec  1.41 KBytes  4567 Kbits/sec  0.226 ms  0/1 (0%)
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.01  sec  1.24 MBytes  9999 Kbits/sec  0.226 ms  6/906 (0.66%)  receiver
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
"""

# only summary available because of client disconnection
CLIENT_DISCO_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 50501
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37963
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1612769692.40 sec  36.8 KBytes  0.00 Kbits/sec  0.097 ms  0/26 (0%)  receiver
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
"""

ZERO_BYTES_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37165
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-0.50   sec  0.00 Bytes  0.00 Kbits/sec  0.000 ms  0/0 (0%)
"""

INTEGER_BITRATE_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37165
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-0.50   sec  0.00 Bytes  0.00 Kbits/sec  0.000 ms  0/0 (0%)
[  5]   1.50-2.00   sec   160 KBytes  2620 Kbits/sec  1.038 ms  0/113 (0%)
"""


IMMEDIATE_DISCO_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1612769692.40 sec  36.8 KBytes  0.00 Kbits/sec  0.097 ms  0/26 (0%)  receiver
"""

CLIENT_BOGUS_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
- - - - - - - - - - - - - - - - - - - - - - - - -
WARNING:  Size of data read does not correspond to offered length
"""

CLIENT_CRASH_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 51513
iperf3: the client has unexpectedly closed the connection
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
"""

CLIENT_KILLED_INPUT = """-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.5.5.2, port 60961
[  5] local 10.5.5.1 port 5201 connected to 10.5.5.2 port 37165
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-0.50   sec  0.00 Bytes  0.00 Kbits/sec  0.000 ms  0/0 (0%)
[  6]  95.50-96.00  sec  63.6 KBytes  1043 Kbits/sec  0.487 ms  0/45 (0%)  
[  6]  95.50-96.00  sec  63.6 KBytes  1043 Kbits/sec  0.487 ms  0/45 (0%)  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  6]   0.00-96.00  sec  11.9 MBytes  1037 Kbits/sec  0.256 ms  32/8623 (0.37%)  receiver
iperf3: the client has terminated
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
"""



class TestStateMachine(unittest.TestCase):
    def _plug_and_chug(self, input_data, state_machine):
        """Feed"""
        lines = [l for l in input_data.split('\n') if l]
        for line in lines:
            state_machine.receive_line(line)

    def test_simple(self):
        mock_bitrate_subscriber = Mock(return_value=None)
        mock_bitrate_summary_subscriber = Mock(return_value=None)
        mock_listening_subscriber = Mock(return_value=None)
        mock_jitter_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_subscriber=mock_bitrate_subscriber,
            bitrate_summary_subscriber=mock_bitrate_summary_subscriber,
            jitter_subscriber=mock_jitter_subscriber,
            listening_subscriber=mock_listening_subscriber)
        self._plug_and_chug(SIMPLE_INPUT, state_machine)

        # verify the bitrate updates came through
        mock_bitrate_subscriber.assert_has_calls(
            [call(1042.0, 'K'), call(1081.0, 'K')])
        self.assertEqual(2, len(mock_bitrate_subscriber.mock_calls))

        # verify bitrate summary
        mock_bitrate_summary_subscriber.assert_has_calls([call(1041.0, 'K')])
        self.assertEqual(1, len(mock_bitrate_summary_subscriber.mock_calls))

        # verify jitter
        mock_jitter_subscriber.assert_has_calls([call(0.598), call(0.226)])
        self.assertEqual(2, len(mock_jitter_subscriber.mock_calls))

        # verify listening
        self.assertEqual(2, len(mock_listening_subscriber.mock_calls))

    def test_truncated(self):
        mock_bitrate_subscriber = Mock(return_value=None)
        mock_bitrate_summary_subscriber = Mock(return_value=None)
        mock_listening_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_subscriber=mock_bitrate_subscriber,
            bitrate_summary_subscriber=mock_bitrate_summary_subscriber,
            listening_subscriber=mock_listening_subscriber)
        self._plug_and_chug(CLIENT_DISCO_INPUT, state_machine)

        mock_bitrate_subscriber.assert_not_called()
        mock_bitrate_summary_subscriber.assert_has_calls([call(0.0, 'K')])
        self.assertEqual(1, len(mock_bitrate_summary_subscriber.mock_calls))
        self.assertEqual(2, len(mock_listening_subscriber.mock_calls))
        
    def test_reconnected(self):
        mock_bitrate_subscriber = Mock(return_value=None)
        mock_bitrate_summary_subscriber = Mock(return_value=None)
        mock_listening_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_subscriber=mock_bitrate_subscriber,
            bitrate_summary_subscriber=mock_bitrate_summary_subscriber,
            listening_subscriber=mock_listening_subscriber)
        self._plug_and_chug(RECONNECTED_INPUT, state_machine)

        # verify the bitrate updates came through
        mock_bitrate_subscriber.assert_has_calls(
            [call(1042.0, 'K'), call(1081.0, 'K'),
                call(1234.0, 'K'), call(4567.0, 'K')])
        self.assertEqual(4, len(mock_bitrate_subscriber.mock_calls))
        mock_bitrate_summary_subscriber.assert_has_calls(
                [call(1041.0, 'K'), call(9999.0, 'K')])
        self.assertEqual(2, len(mock_bitrate_summary_subscriber.mock_calls))
        self.assertEqual(3, len(mock_listening_subscriber.mock_calls))

    def test_zero_bitrate(self):
        mock_bitrate_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_subscriber=mock_bitrate_subscriber)
        self._plug_and_chug(ZERO_BYTES_INPUT, state_machine)

        mock_bitrate_subscriber.assert_has_calls([call(0.0, 'K')])

    def test_integer_bitrate(self):
        mock_bitrate_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_subscriber=mock_bitrate_subscriber)
        self._plug_and_chug(INTEGER_BITRATE_INPUT, state_machine)

        mock_bitrate_subscriber.assert_has_calls([call(0.0, 'K')])

    def test_immediate_disco(self):
        mock_bitrate_summary_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_summary_subscriber=mock_bitrate_summary_subscriber)
        self._plug_and_chug(IMMEDIATE_DISCO_INPUT, state_machine)
        mock_bitrate_summary_subscriber.assert_has_calls([call(0.0, 'K')])
        self.assertEqual(1, len(mock_bitrate_summary_subscriber.mock_calls))

    def test_client_bogus(self):
        mock_bitrate_summary_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_summary_subscriber=mock_bitrate_summary_subscriber)
        self._plug_and_chug(CLIENT_BOGUS_INPUT, state_machine)
        self.assertEqual(0, len(mock_bitrate_summary_subscriber.mock_calls))

    def test_client_crash(self):
        mock_bitrate_summary_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_summary_subscriber=mock_bitrate_summary_subscriber)
        self._plug_and_chug(CLIENT_CRASH_INPUT, state_machine)
        self.assertEqual(0, len(mock_bitrate_summary_subscriber.mock_calls))

    def test_client_killed(self):
        mock_bitrate_summary_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_summary_subscriber=mock_bitrate_summary_subscriber)
        self._plug_and_chug(CLIENT_KILLED_INPUT, state_machine)
        mock_bitrate_summary_subscriber.assert_has_calls([call(1037.0, 'K')])
        self.assertEqual(1, len(mock_bitrate_summary_subscriber.mock_calls))


if __name__ == '__main__':
    unittest.main()
