from discord.ext import tasks, commands

class FetchLoop:
    def __init__(self, channel, subreddit, sort_type, interval, fn):
        self.fetch_loop.change_interval(hours=float(interval))
        self.fetch_loop.start(channel, subreddit, sort_type)
        self.fn = fn

    @tasks.loop(hours=1)
    async def fetch_loop(self, channel, subreddit, sort_type):
        embed = self.fn(subreddit, sort_type)
        await channel.send(embed=embed)