#!/usr/bin/env python

#import asyncio
#import websockets
#import json
import asyncpraw
import datetime
import random
import asyncio
from quart import Quart, jsonify, request

NUMBER_OF_CACHED_IMAGES = 10
NUMBER_OF_POSTS_TO_FETCH = 5

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

# TODO: only images
async def fetch_motivators():
    print('fetch')
    with asyncpraw.Reddit(
        client_id="PTDWkgFFaCdNzEvpgQUXJw",
        client_secret="kl2pLpSFlDDHdSBVJjRNFfkn7WmF-A",
        user_agent="GooDeeBot",
    ) as reddit:
        for subreddit in motivator_subreddits:
            subreddit_aw = await reddit.subreddit(subreddit)
            print(f'fetch {subreddit}')
            async for submission in subreddit_aw.top("all", limit=NUMBER_OF_POSTS_TO_FETCH):
                print(f'fetch url {submission.url}')
                if submission.url.endswith(image_extensions):
                    print(f'yield url {submission.url}')
                    yield submission
                    #motivators_cached.append(submission)


async def generate_motivators():
    async_generator = fetch_motivators()
    post = await async_generator.__anext__()
    print(post.title)
    motivators_cached.append(post)


@app.route("/")
async def hello():
    # return await render_template("index.html")
    #app.add_background_task(generate_motivators)
    await generate_motivators()
    return "hello"


@app.route("/motivate")
async def json():
    # if len(motivators_cached) == 0:
    #    await fetch_motivators()
    random_sub = random.choice(motivators_cached)
    motivators_cached.remove(random_sub)
    return jsonify({'image': random_sub.url})


@app.before_serving
async def startup():
    pass
    #app.background_task = asyncio.ensure_future(generate_motivators())


@app.after_serving
async def shutdown():
    pass
    #app.background_task.cancel()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3031)
