import discord
import json


with open('secrets.json') as secrets_file:
    token = json.load(secrets_file)

with open('settings.json') as settings_file:
    settings = json.load(settings_file)

client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, id=settings['server_id'])
    print(f'{client.user} has connected to Discord!')
    print(f'connected to {guild}')


@client.event
async def on_message(message):
    print(message.channel.id)

client.run(token)
