import os # standard library
import time

import discord # 3rd party packages 
from discord.ext import commands, tasks
import praw
import asyncpraw 
from dotenv import load_dotenv

#import reddit_api # local modules
from loop import MyLoop

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_agent = os.getenv('USER_AGENT')
async_reddit = asyncpraw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# @client.event
# async def on_message(message):
    # if message.author == client.user:
    #     return

#     if message.content.startswith('.hello'):
#         await message.channel.send('Hello!')

@bot.command()
async def subscribe(ctx, arg):
    await ctx.send(f'You have subscribed to {arg}.')

@bot.command()
async def fetch(ctx, sr, st):

    ret_str = __gen_ret_str(sr, st)
    await ctx.send(ret_str)

# TODO: Currently, this only works for one instance, so perhaps creating a separate cog for each call of the command is the right way to do it
@bot.command(name='auto')
async def fetch_auto(ctx, sr, st, interval):
    # fetch_loop.change_interval(hours=float(interval))
    # fetch_loop.start(ctx.channel, sr, st)
    loop = MyLoop(ctx.channel, sr, st, interval, __gen_ret_str)

# TODO: Could potentially use SubredditStream here, but it's blocking? example taken from: https://asyncpraw.readthedocs.io/en/stable/tutorials/reply_bot.html, but it's not working
@bot.command()
async def feed(ctx, sr):

    # ret_str = __gen_ret_str(sr, 'new')
    # await ctx.send(ret_str)
    # feed_loop.start(ctx.channel, sr, time.time())
    sub = await async_reddit.subreddit(sr)
    async for submission in sub.stream.submissions():
        print(submission.title)

@tasks.loop(minutes=15)
async def feed_loop(channel, sr, last_subm_time):
    pass

@bot.command()
async def ping(ctx):
    await ctx.send(f'Your ping is {round(bot.latency * 1000)}ms')

# class MyLoop:
#     def __init__(self, channel, sr, st, interval):
#         self.fetch_loop.change_interval(hours=float(interval))
#         self.fetch_loop.start(channel, sr, st)

#     @tasks.loop(hours=1)
#     async def fetch_loop(self, channel, sr, st):
#         ret_str = __gen_ret_str(sr, st)
#         await channel.send(ret_str)

def __gen_ret_str(sr, st):
    submission_list = []

    if st.lower() == 'new':
        for submission in reddit.subreddit(sr).new(limit=5):
            submission_list.append(submission)
    elif st.lower() == 'top':
        for submission in reddit.subreddit(sr).top(limit=5):
            submission_list.append(submission)
    elif st.lower() == 'hot':
        for submission in reddit.subreddit(sr).hot(limit=5):
            submission_list.append(submission)
    elif st.lower() == 'rising':
        for submission in reddit.subreddit(sr).rising(limit=5):
            submission_list.append(submission)
    
    sub_str = ""
    for submission in submission_list:
        sub_str += f'{submission.score} points | {submission.title} | {submission.url} \n\n '

    ret_str = f"Here are the 5 {st.lower()} posts on {sr}: \n {sub_str}" 

    return ret_str

bot.run(TOKEN)
