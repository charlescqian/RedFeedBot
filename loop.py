from discord.ext import tasks, commands

class FetchLoop:
    def __init__(self, channel, sr, st, interval, fn):
        self.fetch_loop.change_interval(hours=float(interval))
        self.fetch_loop.start(channel, sr, st)
        self.fn = fn

    @tasks.loop(hours=1)
    async def fetch_loop(self, channel, sr, st):
        ret_str = self.fn(sr, st)
        await channel.send(ret_str)