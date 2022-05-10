#!/usr/bin/env python

#import asyncio
#import websockets
#import json
import asyncpraw
import datetime
import random
import asyncio
from quart import Quart, jsonify, request

NUMBER_OF_POSTS_TO_CACHE = 5   # 100 #5 test
NUMBER_OF_POSTS_TO_FETCH = 50  # 1000 #50 test

app = Quart(__name__)
motivators_cached = []
motivator_subreddits = [
    "getdisciplined",
    "GetMotivated",
    "Mindfulness",
    "selfimprovement",
    "confidence"
]
image_extensions = ('.jpg', '.png', '.svg', '.jpeg', '.tif', '.tiff')
random.shuffle(motivator_subreddits)


async def create_generator_from(subreddits):
    with asyncpraw.Reddit(
        client_id="PTDWkgFFaCdNzEvpgQUXJw",
        client_secret="kl2pLpSFlDDHdSBVJjRNFfkn7WmF-A",
        user_agent="GooDeeBot",
    ) as reddit:
        # for subreddit in subreddits:
        i = 0
        while(True):
            subreddit = subreddits[i % len(subreddits)]
            # TODO: overflow
            i += 1
            print(f'fetch {i} number of times')
            subreddit_aw = await reddit.subreddit(subreddit)
            print(f'fetch {subreddit}')
            async for submission in subreddit_aw.top("all", limit=NUMBER_OF_POSTS_TO_FETCH):
                print(f'fetch url {submission.url}')
                if submission.url.endswith(image_extensions):
                    print(f'yield url {submission.url}')
                    yield submission


async def fetch_posts_from(async_generator):
    if (len(motivators_cached) >= NUMBER_OF_POSTS_TO_CACHE):
        return
    post = await async_generator.__anext__()
    print(post.title)
    motivators_cached.append(post)


async def check_motivators():
    async_generator = create_generator_from(motivator_subreddits)
    while(True):
        await fetch_posts_from(async_generator)
        await asyncio.sleep(1)


@app.route("/")
async def hello():
    # return await render_template("index.html")
    # app.add_background_task(fetch_posts_from)
    # await check_motivators()
    return "hello"


@app.route("/motivate")
async def json():
    # if len(motivators_cached) == 0:
    #    await create_generator_from()
    random_sub = random.choice(motivators_cached)
    motivators_cached.remove(random_sub)
    return jsonify({'image': random_sub.url})


@app.before_serving
async def startup():
    app.background_task = asyncio.ensure_future(check_motivators())


@app.after_serving
async def shutdown():
    app.background_task.cancel()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3031)
