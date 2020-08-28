import os # standard library
import time
from datetime import datetime

import discord # 3rd party packages 
from discord.ext import commands, tasks
import praw
import asyncpraw 
from dotenv import load_dotenv
import pymongo

from loop import FetchLoop #local modules

######################## Setup ###########################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_agent = os.getenv('USER_AGENT')
DB_PASSWORD = os.getenv('DB_PASSWORD')

async_reddit = asyncpraw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

client = discord.Client()
bot = commands.Bot(command_prefix='.')

# client = pymongo.MongoClient(f'mongodb+srv://dbAdmin:{DB_PASSWORD}@redfeed.goti6.gcp.mongodb.net/<dbname>?retryWrites=true&w=majority')
# db = client.subscriptions

FETCH_LIMIT = 5

########################## Bot Events ##########################
# TODO: On bot ready, check the DB for any channels that are subscribed 
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    # channel = client.get_channel(745410258142363688)
    # await channel.send('hello')

# TODO: Add more error processing
@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('The command you have entered was not found, please check **.help** for all available commands.')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'You are missing the **{error.param}** argument. Please pass in all required arguments, see **.help {ctx.command}** for more information.')

########################## Bot Commands ##########################

@bot.command(description=f'Fetch {FETCH_LIMIT} posts from the given subreddit, sorted by the given sort type (hot/new/top/rising). Example: ".fetch funny hot" will fetch the {FETCH_LIMIT} hottest posts from r/funny.')
async def fetch(ctx, subreddit, sort_type):
    embed = __gen_embed(subreddit, sort_type)
    await ctx.send(embed=embed)


@bot.command(name='auto', description='Automatically fetch {FETCH_LIMIT} posts from the given subreddit, sorted by the given sort type (hot/new/top/rising), at every given interval (in hours). Example: ".auto funny hot 1" will fetch the {FETCH_LIMIT} hottest posts from r/funny every hour.')
async def auto(ctx, subreddit, sort_type, interval : float):
    loop = FetchLoop(ctx.channel, subreddit, sort_type, interval, __gen_embed)


@bot.command(description='Fetches the {FETCH_LIMIT} newest posts from the given subreddit, then every time a new post is submitted to the subreddit, a message will be sent with the post\'s details. Example: ".feed funny"')
async def feed(ctx, subreddit):
    embed = __gen_embed(subreddit, 'new')
    await ctx.send(embed=embed)
    
    count = 0
    sub = await async_reddit.subreddit(subreddit)
    async for submission in sub.stream.submissions():
        if count < 100: # This removes the 100 historical submissions that SubredditStream pulls.
            count += 1
            continue
        embed = discord.Embed(title=f'Newest post on {subreddit}')
        embed.add_field(name=submission.title, value=f'{submission.score} points | [Link]({submission.url}) | [Comments](https://www.reddit.com/r/{subreddit}/comments/{submission.id})', inline=False)
        await ctx.send(embed=embed)

@bot.command(hidden='true')
async def ping(ctx):
    await ctx.send(f'Your ping is {round(bot.latency * 1000)}ms')

# TODO: Maybe a command to get comments from a post? 

############################ Helper Functions #################################
# TODO: Find a way to better format the strings, maybe add some hyperlinks rather then posting the whole link
def __gen_ret_str(subreddit, sort_type):
    submission_list = []

    if sort_type.lower() == 'new':
        for submission in reddit.subreddit(subreddit).new(limit=FETCH_LIMIT):
            submission_list.append(submission)
    elif sort_type.lower() == 'top':
        for submission in reddit.subreddit(subreddit).top(limit=FETCH_LIMIT):
            submission_list.append(submission)
    elif sort_type.lower() == 'hot':
        for submission in reddit.subreddit(subreddit).hot(limit=FETCH_LIMIT):
            submission_list.append(submission)
    elif sort_type.lower() == 'rising':
        for submission in reddit.subreddit(subreddit).rising(limit=FETCH_LIMIT):
            submission_list.append(submission)
    
    sub_str = ""
    for submission in submission_list:
        sub_str += f'{submission.score} points | {submission.title} | [Link]({submission.url}) \n\n '

    ret_str = f"Here are the {FETCH_LIMIT} {sort_type.lower()} posts on {subreddit}: \n {sub_str}" 

    return ret_str

def __gen_embed(subreddit, sort_type):
    submission_list = []

    if sort_type.lower() == 'new':
        for submission in reddit.subreddit(subreddit).new(limit=FETCH_LIMIT):
            submission_list.append(submission)
    elif sort_type.lower() == 'top':
        for submission in reddit.subreddit(subreddit).top(limit=FETCH_LIMIT):
            submission_list.append(submission)
    elif sort_type.lower() == 'hot':
        for submission in reddit.subreddit(subreddit).hot(limit=FETCH_LIMIT):
            submission_list.append(submission)
    elif sort_type.lower() == 'rising':
        for submission in reddit.subreddit(subreddit).rising(limit=FETCH_LIMIT):
            submission_list.append(submission)

    embed = discord.Embed(title=f'{FETCH_LIMIT} {sort_type.lower()} posts on {subreddit}')
    for submission in submission_list:
        embed.add_field(name=submission.title, value=f'{submission.score} points | [Link]({submission.url}) | [Comments](https://www.reddit.com/r/{subreddit}/comments/{submission.id}) | Submitted at {time.ctime(submission.created_utc)}', inline=False)
    
    return embed


bot.run(TOKEN)