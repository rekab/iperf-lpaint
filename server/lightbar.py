import asyncio
import board
import adafruit_dotstar as dotstar

NUM_PIXELS = 73
BRIGHTNESS = 0.5


UNIT_MULTIPLIER = {
        '': (1.0/1024.0),
        'K': 1.0,
        'M': 1024.0,
        'G': 1024.0 * 1024.0,
        }

MAX_BITRATE = 1300.0 * UNIT_MULTIPLIER['K']
MAX_JITTER = 100.0

# how wide the cylon-esque red light thing is
RED_BAND_WIDTH = 5


def kbyte_rgb(value, minimum=0.0, maximum=MAX_JITTER):
    # Sanity check
    if value > maximum:
        print(f'value {value} exceeds maximum {maximum}')
        maximum = value

    minimum, maximum = float(minimum), float(maximum)

    green_ratio = pow((value - minimum), 2.3) / (maximum - minimum)
    blue_ratio = pow((value - minimum) / (maximum - minimum), 1.3)
    #red_ratio = pow((value - minimum), 1.4) / (maximum - minimum)

    g = min(255, int(max(0, 255*(1 - green_ratio))))
    b = min(255, int(max(0, 255*(1 - blue_ratio))))
    r = min(255, int(max(0, 255 - (.3*g) - (.7*b))))
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
        color = kbyte_rgb(bitrate, maximum=MAX_BITRATE)
        print(f'bitrate={bitrate} color={color}')
        self.dots.fill(color)

    def jitter_subscriber(self, jitter_ms):
        if self.animation_task is not None:
            print('canceling animation task')
            self.animation_task.cancel()
            self.animation_task = None

        color = kbyte_rgb(jitter_ms, maximum=MAX_JITTER)
        print(f'jitter_ms={jitter_ms} color={color}')
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
