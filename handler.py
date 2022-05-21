#!/usr/bin/env python

#import asyncio
#import websockets
#import json
import asyncpraw
import datetime
import random
import asyncio
from quart import Quart, jsonify, request

NUMBER_OF_POSTS_TO_CACHE = 100   # 100 #prod #5 test
NUMBER_OF_POSTS_TO_FETCH = 1000  # 1000 #prod #50 test

app = Quart(__name__)
motivators_cached = []
motivator_subreddits = [
    "getdisciplined",
    "GetMotivated",
    "Mindfulness",
    "selfimprovement",
    "confidence"
]
funny_cached = []
funny_subreddits = [
    "funny",
    "humor",
    "hilarious",
    "lol",
    "lmao",
    "anythinggoescomedy",
    "actuallyfunny",
    "FunnyRedditTime"
]
memes_cached = []
memes_subreddits = [
    "memes",
    "AdviceAnimals",
    "AdviceAnimals+funny+memes",
    "funny",
    "PrequelMemes",
    "SequelMemes",
    "MemeEconomy",
    "ComedyCemetery",
    "PewdiepieSubmissions",
    "dankmemes",
    "terriblefacebookmemes",
    "shittyadviceanimals",
    "wholesomememes",
    "me_irl",
    "2meirl4meirl",
    "i_irl",
    "meirl",
    "BikiniBottomTwitter",
    "trippinthroughtime",
    "boottoobig",
    "HistoryMemes",
    "fakehistoryporn",
    "OTMemes",
    "starterpacks",
    "gifs",
    "rickandmorty",
    "FellowKids",
    "Memes_Of_The_Dank",
    "raimimemes",
    "comedyhomicide",
    "lotrmemes",
    "freefolk",
    "GameOfThronesMemes",
    "howyoudoin",
    "HolUp",
    "meme",
    "memeswithoutmods",
    "dankmeme",
    "suicidebywords",
    "puns",
    "PerfectTiming"
]
# pepethefrog, Pepe_Memes, 4chan
culture_cached = []
culture_subreddits = [
    "Animewallpaper",
    "NSFWAnimeWallpaper",
    "animemidriff",
    "AlmostHentai",
    "OfficialSenpaiHeat",
    "AnimeLingerie",
    "Sukebei",
    "animelegs",
    "buttfangs",
    "skindentation",
    "HentaiCleavage",
    "UpskirtHentai",
    "ecchi",
    "ecchigifs",
    "thighdeology",
    "ZettaiRyouiki",
    "Ecchibondage",
    "Fitmoe",
    "fitdrawngirls",
]
# TODO: gifs?
image_extensions = ('.jpg', '.png', '.svg', '.jpeg', '.tif', '.tiff')


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


async def fetch_posts_from(async_generator, array_cached):
    if (len(array_cached) >= NUMBER_OF_POSTS_TO_CACHE):
        return
    post = await async_generator.__anext__()
    print(post.title)
    array_cached.append(post)


async def fetch_generator_with_pause(subreddits, array_cached):
    random.shuffle(subreddits)
    async_generator = create_generator_from(subreddits)
    while(True):
        await fetch_posts_from(async_generator, array_cached)
        await asyncio.sleep(1)


@app.route("/")
async def hello():
    # return await render_template("index.html")
    # app.add_background_task(fetch_posts_from)
    # await fetch_generator_with_pause()
    return "hello"


@app.route("/funny")
async def json1():
    random_sub = random.choice(funny_cached)
    funny_cached.remove(random_sub)
    return jsonify({'image': random_sub.url})

@app.route("/motivate")
async def json2():
    # if len(motivators_cached) == 0:
    #    await create_generator_from()
    random_sub = random.choice(motivators_cached)
    motivators_cached.remove(random_sub)
    return jsonify({'image': random_sub.url})

@app.route("/meme")
async def json3():
    random_sub = random.choice(memes_cached)
    memes_cached.remove(random_sub)
    return jsonify({'image': random_sub.url})

@app.route("/culture")
async def json4():
    random_sub = random.choice(culture_cached)
    culture_cached.remove(random_sub)
    return jsonify({'image': random_sub.url})


@app.before_serving
async def startup():
    app.background_task1 = asyncio.ensure_future(
        fetch_generator_with_pause(funny_subreddits, funny_cached))
    app.background_task2 = asyncio.ensure_future(
        fetch_generator_with_pause(motivator_subreddits, motivators_cached))
    app.background_task3 = asyncio.ensure_future(
        fetch_generator_with_pause(memes_subreddits, memes_cached))
    app.background_task4 = asyncio.ensure_future(
        fetch_generator_with_pause(culture_subreddits, culture_cached))


@app.after_serving
async def shutdown():
    app.background_task1.cancel()
    app.background_task2.cancel()
    app.background_task3.cancel()
    app.background_task4.cancel()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3031)
