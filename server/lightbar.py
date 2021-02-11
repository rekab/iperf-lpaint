import asyncio
import board
import adafruit_dotstar as dotstar

NUM_PIXELS = 73
BRIGHTNESS = 0.09


UNIT_MULTIPLIER = {
        'K': 1.0,
        'M': 1024.0,
        'G': 1024.0 * 1024.0,
        }

# TODO: max bitrate should be calibrated
MAX_BITRATE = 3000 * UNIT_MULTIPLIER['K']


def kbyte_rgb(value, minimum=0.0, maximum=MAX_BITRATE):
    # Sanity check
    if value > maximum:
        print(f'value {value} exceeds maximum {maximum}')
        maximum = value

    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    r = int(max(0, 255*(ratio - 1)))
    g = 255 - b - r
    return (r, g, b)


async def listenloop():
    try:
        while True:
            print('still listening...')
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print('listenloop canceled')


class DotPainter(object):
    def __init__(self,
            num_pixels: int=NUM_PIXELS,
            brightness: float=BRIGHTNESS):
        self.num_pixels = num_pixels
        self.dots = dotstar.DotStar(
                board.SCK, board.MOSI, num_pixels, brightness=brightness)
        self.animation_task = None

    def bitrate_subscriber(self, bitrate, bitrate_unit):
        if self.animation_task is not None:
            print('canceling animation task')
            self.animation_task.cancel()
            self.animation_task = None

        bitrate *= UNIT_MULTIPLIER[bitrate_unit]
        color = kbyte_rgb(bitrate)
        print(f'bitrate={bitrate} color={color}')
        self.dots.fill(color)

    def listening_subscriber(self):
        print('listening...')
        if self.animation_task is not None:
            # This can happen if the client disconnects before any bitrate info
            # can be sent
            print('never turned off animation task')
            return
        #self.dots.fill((0, 0, 0))
        loop = asyncio.get_running_loop()
        self.animation_task = loop.create_task(listenloop())


# TODO: connected/disconnected subscriber
