import discord
from discord.ext import commands
import json
import sqlite3
from sqlite3 import Error
from difflib import SequenceMatcher
import time


connection = sqlite3.connect('games.sqlite')
one, two, three, no = ["1️⃣", "2️⃣", "3️⃣", "🚫"]
reactions = [one, two, three, no]
message_cache = {}


async def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(e)


async def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(e)


async def get_games(connection):
    games_query = "SELECT * from games"
    games = await execute_read_query(connection, games_query)
    return games


async def add_game(connection, game, uids):
    query = insert_game_into_table.format(
                title=game, uids=uids)
    await execute_query(connection, query)


create_games_table = """
CREATE TABLE IF NOT EXISTS games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  uids TEXT
);
"""

insert_game_into_table = """
INSERT INTO
  games (name, uids)
VALUES
  ('{title}', '{uids}');
"""


with open('secrets.json') as secrets_file:
    token = json.load(secrets_file)

with open('settings.json') as settings_file:
    settings = json.load(settings_file)

bot = commands.Bot(command_prefix='!')


async def alike(a, b):
    return SequenceMatcher(None, a, b).ratio()


async def findalike(query, lst):
    games = []
    for game in lst:
        score = await alike(query, game)
        games.append((score, game))
    return games


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=settings['server_id'])
    channel = discord.utils.get(guild.channels, id=settings['channel_id'])
    print(f'{bot.user.name} has connected to Discord!')
    print(f'connected to {guild}')
    print(f'connected to {channel}')
    await execute_query(connection, create_games_table)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


# @bot.event
# async def on_message(message):
#     print("Message received")
#     bot_id = settings.get('bot_id')
#     sender = message.author.id
#     print("IDs checked")
#     if sender == bot_id:
#         print(message)


@bot.event
async def on_reaction_add(reaction, user):
    if user.id == settings.get('bot_id'):
        return
    elif not message_cache.get(reaction.message.id):
        return
    if reaction == one:
        pass
    elif reaction == two:
        pass
    elif reaction == three:
        pass
    elif reaction == no:
        pass


@bot.command(name='addgame', help='Place a game up for trades')
async def addgame(ctx):
    game = ctx.message.content[9:]
    member = ctx.message.author
    await member.create_dm()
    games = await get_games(connection)
    games_stripped = [existing[1] for existing in games]
    hits = await findalike(game, games_stripped)
    hits.sort()
    if hits:
        hitlist = [hit[1] for hit in hits[:-4:-1]]
        message_list = [f"{str(i+1)}.\t{hit[1]}" for i,
                        hit in enumerate(hitlist)]
        response = await member.dm_channel.send(
              "Is your game one of the following?\n" + "\n".join(message_list))
        now = time.time()
        delete_these = []
        for key, value in message_cache.items():
            if now - value[-1] > 30:
                delete_these.append[key]
        for key in delete_these:
            del message_cache[key]
        message_cache[response.id] = [*hitlist, now]
        await response.add_reaction(one)
        await response.add_reaction(two)
        await response.add_reaction(three)
        await response.add_reaction(no)

    # response = await member.dm_channel.send(f'Really add {game}?')
    # await response.add_reaction('👍')
    # await response.add_reaction('👎')
    # await add_game(connection, game, member.id)

bot.run(token)
