import os # standard library

import discord # 3rd party packages 
from discord.ext import commands, tasks
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
        sub_str += f'{submission.score} points | {submission.title} | {submission.url} \n\n '

    ret_str = f"Here are the 5 {args[1].lower()} posts on {args[0]}: \n {sub_str}" 
    await ctx.send(ret_str)

# TODO: Currently, this only works for one instance, so perhaps creating a separate cog for each call of the command is the right way to do it
@client.command(aliases=['auto'])
async def fetch_auto(ctx, *args):

    fetch_loop.change_interval(hours=float(args[2]))
    fetch_loop.start(ctx.channel, args[0], args[1])
    #auto_fetch_cog = AutoFetchCog(args[0], args[1], args[2])

@client.command()
async def ping(ctx):
    await ctx.send(f'Your ping is {round(client.latency * 1000)}ms')

@tasks.loop(hours=1)
async def fetch_loop(channel, sr, sort_type):
    submission_list = []

    if sort_type.lower() == 'new':
        for submission in reddit.subreddit(sr).new(limit=5):
            submission_list.append(submission)
    elif sort_type.lower() == 'top':
        for submission in reddit.subreddit(sr).top(limit=5):
            submission_list.append(submission)
    elif sort_type.lower() == 'hot':
        for submission in reddit.subreddit(sr).hot(limit=5):
            submission_list.append(submission)
    elif sort_type.lower() == 'rising':
        for submission in reddit.subreddit(sr).rising(limit=5):
            submission_list.append(submission)
    
    sub_str = ""
    for submission in submission_list:
        sub_str += f'{submission.score} points | {submission.title} | {submission.url} \n\n '

    ret_str = f"Here are the 5 {sort_type.lower()} posts on {sr}: \n {sub_str}" 

    await channel.send(ret_str)


# class AutoFetchCog(commands.Cog):
#     def __init__(self, subreddit, sort_type, period):
#         self.subreddit = subreddit
#         self.sort_type = sort_type
#         self.period = period
#         self.printer.start()

#     @tasks.loop(seconds=10)
#     async def printer(self):
#         print(self.subreddit)
#         print(self.sort_type)
#         print(self.period)


client.run(TOKEN)