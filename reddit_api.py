import os

import praw 
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
user_agent = os.getenv('USER_AGENT')
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

print(reddit.read_only)

for submission in reddit.subreddit("bapcsalescanada").new(limit=10):
    print(submission.title)
    print(submission.url)
    print(submission.id)


