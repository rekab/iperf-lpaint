import lightbar

from aiohttp import web


class Handler(object):
    def __init__(self, state_machine, dotpainter):
        self.state_machine = state_machine
        self.dotpainter = dotpainter

    async def status(self, request):
        lines = '\n'.join(self.state_machine.get_line_buffer())
        return web.Response(
                body=f'state={self.state_machine.get_state()}\n'
                f'buffer:\n{lines}')
