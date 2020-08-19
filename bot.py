import os # standard library

import discord # 3rd party packages 
from discord.ext import commands 
import praw 
from dotenv import load_dotenv

#import reddit_api # local modules

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_agent = os.getenv('USER_AGENT')
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

client = commands.Bot(command_prefix='.')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# @client.event
# async def on_message(message):
    # if message.author == client.user:
    #     return

#     if message.content.startswith('.hello'):
#         await message.channel.send('Hello!')

@client.command()
async def subscribe(ctx, arg):
    await ctx.send(f'You have subscribed to {arg}.')

@client.command()
async def fetch(ctx, *args):
    if len(args) != 2:
        await ctx.send('This command requires 2 arguments, please try again with \".fetch (subreddit) (sort type ie. new/top/hot/rising)\"')
    submission_list = []
    if args[1].lower() == 'new':
        for submission in reddit.subreddit(args[0]).new(limit=5):
            submission_list.append(submission)
            print(submission.title)
            print(submission.url)
            print(submission.id)
    elif args[1].lower() == 'top':
        for submission in reddit.subreddit(args[0]).top(limit=5):
            submission_list.append(submission)
            print(submission.title)
            print(submission.url)
            print(submission.id)
    elif args[1].lower() == 'hot':
        for submission in reddit.subreddit(args[0]).hot(limit=5):
            submission_list.append(submission)
            print(submission.title)
            print(submission.url)
            print(submission.id)
    elif args[1].lower() == 'rising':
        for submission in reddit.subreddit(args[0]).rising(limit=5):
            submission_list.append(submission)
    else: 
        await ctx.send('The specified sort type does not exist or is not available.')

    sub_str = ""
    for submission in submission_list:
        sub_str += f'{submission.score} points {submission.title}  {submission.url} \n\n '

    ret_str = f"Here are the 5 {args[1]} posts on {args[0]}: \n {sub_str}" 
    await ctx.send(ret_str)
@client.command()
async def ping(ctx):
    await ctx.send(f'Your ping is {round(client.latency * 1000)}ms')

client.run(TOKEN)