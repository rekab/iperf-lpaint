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

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _plug_and_chug(self, input_data, state_machine):
        """Feed"""
        #lines = [l + '\n' for l in input_data.split('\n')
        for line in lines:
            state_machine.receive_line(line)

    def test_simple_bitrate(self):
        mock_bitrate_subscriber = Mock(return_value=None)
        state_machine = iperf3_output_state.IperfServerStateDriver(
            bitrate_subscriber=mock_bitrate_subscriber)
        self._plug_and_chug(SIMPLE_INPUT, state_machine)

        # verify the bitrate updates came through
        mock_bitrate_subscriber.assert_has_calls(
            call(1042), call(1081))
