import atexit
import asyncio
import os
import iperf3_output_state
import lightbar


# iperf3  -B 10.5.5.1 -s -i .5 -f k --forceflush
IPERF3_SERVER_COMMAND = [
    #'/usr/bin/iperf3',
    '/home/pi/download/iperf-3.9/src/iperf3',
    '-B', '10.5.5.1',   # bind to wlan ip
    '-s',               # server
    '-i', '0.5',        # print stats every .5 seconds
    '-f', 'k',          # print kilobytes
    '--forceflush',     # flush output for consumption
  ]


async def read_iperf_proc(proc, state_machine, killer_lambda):
    while True:
        data = await proc.stdout.readline()
        line = data.decode('ascii').rstrip()
        print(f'read line: {line}')
        state_machine.receive_line(line)
        if proc.stdout.at_eof():
            print('stdout eof')
            break
    if proc.returncode != 0:
        print('iperf failure!!! returncode:', returncode)
    atexit.unregister(killer_lambda)


class DeadConnectionMonitor(object):
    """Watches for too many zeros.

    If the iperf client can't reach the server because it fell off wifi, iperf
    may keep waiting indefinitely.
    """

    def __init__(self, iperf_pid, max_num_zero_byte_transfers=30):
        self.iperf_pid = iperf_pid
        self.max_num_zero_byte_transfers = max_num_zero_byte_transfers
        self.num_sequential_zero_byte_transfers = 0
        self.prev_transfer = None

    def transfer_subscriber(self, num_bytes, unit):
        if num_bytes == 0.0:
            if self.prev_transfer == 0.0:
                self.num_sequential_zero_byte_transfers += 1
        else:
            self.num_sequential_zero_byte_transfers = 1

        if self.num_sequential_zero_byte_transfers >= self.max_num_zero_byte_transfers:
            print(f'killing iperf pid {self.iperf_pid}')
            os.kill(self.iperf_pid, 15)
        self.prev_transfer = num_bytes


async def run_iperf_server():
    dotpainter = lightbar.DotPainter()
    proc = await asyncio.create_subprocess_exec(
        *IPERF3_SERVER_COMMAND,
        stdout=asyncio.subprocess.PIPE)
    print("Started: %s, pid=%s" % (IPERF3_SERVER_COMMAND, proc.pid), flush=True)
    killer_lambda = lambda pid: os.kill(proc.pid, 15)
    atexit.register(killer_lambda, proc.pid)


    state_machine = iperf3_output_state.IperfServerStateDriver(
            #bitrate_subscriber=dotpainter.bitrate_subscriber,
            jitter_subscriber=dotpainter.jitter_subscriber,
            listening_subscriber=dotpainter.listening_subscriber)


    await asyncio.wait([read_iperf_proc(proc, state_machine, killer_lambda)])


asyncio.run(run_iperf_server())
