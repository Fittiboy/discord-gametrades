import discord
from discord.ext import commands
import json
import sqlite3
from sqlite3 import Error
from difflib import SequenceMatcher


connection = sqlite3.connect('games.sqlite')


async def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(e)


create_games_table = """
CREATE TABLE IF NOT EXISTS games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  uids TEXT
);
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
#     member = message.author
#     if member == bot.user:
#         return
#     await member.create_dm()
#     await member.dm_channel.send("HI")


@bot.command(name='addgame', help='Place a game up for trades')
async def addgame(ctx):
    game = ctx.message.content[9:]
    member = ctx.message.author
    await member.create_dm()
    await member.dm_channel.send(f'Really add {game}?')
    pass

bot.run(token)
