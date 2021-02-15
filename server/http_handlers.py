from aiohttp import web


class Handler(object):
    def __init__(self):
        pass

    async def status(self, request):
        return web.Response(body="asdf")

