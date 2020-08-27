import os # standard library
import time

import discord # 3rd party packages 
from discord.ext import commands, tasks
import praw
import asyncpraw 
from dotenv import load_dotenv

from loop import MyLoop #local modules

######################## Setup ###########################
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

########################## Bot Commands ##########################
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(description='Fetch 5 posts from the given subreddit, sorted by the given sort type (hot/new/top/rising). Example: \".fetch funny hot\" will fetch the 5 hottest posts from r/funny.')
async def fetch(ctx, subreddit, sort_type):
    ret_str = __gen_ret_str(subreddit, sort_type)
    await ctx.send(ret_str)

@bot.command(name='auto', description='Automatically fetch 5 posts from the given subreddit, sorted by the given sort type (hot/new/top/rising), at every given interval (in hours). Example: \".auto funny hot 1\" will fetch the 5 hottest posts from r/funny every hour.')
async def fetch_auto(ctx, subreddit, sort_type, interval):
    loop = MyLoop(ctx.channel, subreddit, sort_type, interval, __gen_ret_str)

@bot.command(description='Fetches the 5 newest posts from the given subreddit, then every time a new post is submitted to the subreddit, a message will be sent with the post\'s details. Example: \".feed funny\"')
async def feed(ctx, subreddit):

    ret_str = __gen_ret_str(subreddit, 'new')
    await ctx.send(ret_str)
    
    count = 0
    sub = await async_reddit.subreddit(subreddit)
    async for submission in sub.stream.submissions():
        if count < 100:
            count += 1
            continue
        sub_str = f'Here is the latest post on {subreddit}: {submission.score} points | {submission.title} | {submission.url}'
        await ctx.send(sub_str)

@bot.command(hidden='true')
async def ping(ctx):
    await ctx.send(f'Your ping is {round(bot.latency * 1000)}ms')


############################ Helper Functions #################################
# TODO: Find a way to better format the strings, maybe add some hyperlinks rather then posting the whole link
def __gen_ret_str(subreddit, sort_type):
    submission_list = []

    if sort_type.lower() == 'new':
        for submission in reddit.subreddit(subreddit).new(limit=5):
            submission_list.append(submission)
    elif sort_type.lower() == 'top':
        for submission in reddit.subreddit(subreddit).top(limit=5):
            submission_list.append(submission)
    elif sort_type.lower() == 'hot':
        for submission in reddit.subreddit(subreddit).hot(limit=5):
            submission_list.append(submission)
    elif sort_type.lower() == 'rising':
        for submission in reddit.subreddit(subreddit).rising(limit=5):
            submission_list.append(submission)
    
    sub_str = ""
    for submission in submission_list:
        sub_str += f'{submission.score} points | {submission.title} | {submission.url} \n\n '

    ret_str = f"Here are the 5 {sort_type.lower()} posts on {subreddit}: \n {sub_str}" 

    return ret_str

# TODO: Maybe a copmmand to get comments from a post? 


bot.run(TOKEN)