import asyncio
import board
import adafruit_dotstar as dotstar

NUM_PIXELS = 73
BRIGHTNESS = 0.09


UNIT_MULTIPLIER = {
        '': (1.0/1024.0),
        'K': 1.0,
        'M': 1024.0,
        'G': 1024.0 * 1024.0,
        }

# max was calibrated at home
MAX_BITRATE = 20000 * UNIT_MULTIPLIER['K']

# how wide the cylon-esque red light thing is
RED_BAND_WIDTH = 5


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


async def listenloop(dots, num_pixels):
    reds_down = [
            (r, int(r*r/2000), int((r*r)/2755))
            for r in range(0, 255, int(255/RED_BAND_WIDTH))]
    reds_up = reds_down[:]
    reds_up.reverse()
    reds = reds_down + reds_up
    num_reds = len(reds)
    direction = 1
    start = 0
    try:
        while True:
            for red_idx in range(0, len(reds), 1):
                dots[start + red_idx] = reds[red_idx]

            start += direction
            if start+len(reds) >= num_pixels or start <= 0:
                direction *= -1
                start += 2*direction

            await asyncio.sleep(.02)
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
        self.dots.fill((0, 0, 0))
        loop = asyncio.get_running_loop()
        self.animation_task = loop.create_task(
                listenloop(self.dots, self.num_pixels))
