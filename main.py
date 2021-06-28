import discord
import os
import json
import asyncio
import random
import requests
from urlextract import URLExtract
import selfbot
import urllib3

"""
Initialization
"""

TOKEN = 'ODU4MDA0MzQ2MDQyMzE4ODQ5.YNX00Q.8vEhPteid_rWmFhDADhvNSEnpfk'
SOURCE_CHANNEL_ID = 796166200555470878
ex = URLExtract()

client_servers = []

client = discord.Client()

if not os.path.isfile('./cache.json'):
    with open('./cache.json', 'w+') as f:
        f.write('[]')
        f.close()
"""
On Startup
"""


@client.event
async def on_ready():
    # Get all of the servers that the bot is a member of and add them to a list
    print(f"{client.user} has connected to Discord")
    print(f"{client.user} is currently connected to {len(client.guilds)} servers")



@client.event
async def on_message(message):
    """
    Bot Commands
    """
    if message.content == '**clean**':
        message_history = await message.channel.history(limit=10000).flatten()
        print("Deleting the last ten-thousand messages")
        for message in message_history:
            if message.author == client.user:
                await message.delete()


"""
Main Check-Updates Loop
"""


async def update_site():
    while True:
        print("Looping...")

        # Get the most recent state of the source channel from the selfbot account
        recent_list = selfbot.retrieve_messages(SOURCE_CHANNEL_ID)

        # Compare that to the stored version of the state of the source channel
        for server in client.guilds:
            print(server.name)
            if server.name == 'Icy Exchange':
                for channel in server.channels:
                    if channel.name == '💾│packs':
                        # Get a list of all messages sent
                        messages_sent = await channel.history(limit=10000).flatten()

                        # Get a list of all messages sent by the bot
                        urls_sent_by_bot = []
                        for message in messages_sent:
                            if message.author == client.user:
                                for url in ex.find_urls(message.content):
                                    urls_sent_by_bot.append(url)

                        print(urls_sent_by_bot)

                        # Parse every message in the recent list
                        message_content = []
                        for message in recent_list:
                            message_string = message['content']
                            try:
                                message_string = message_string.replace('@everyone', '')
                            except:
                                print('message did not contain @everyone')

                            try:
                                message_string = message_string.replace('join our groups for more : ', '')
                            except:
                                print('message did not have a group ad')

                            urls = ex.find_urls(message_string)
                            for url in urls:
                                if 'pastelink' in url:
                                    message_string = message_string.replace(url, '')
                                if 'bit.ly' in url:
                                    print(f"Resolving url: {url}")
                                    if not selfbot.pull_link_from_cache(url):
                                        resolved_url = selfbot.resolve_bitly_to_mega(url)
                                        selfbot.add_link_to_cache(url, resolved_url)
                                    else:
                                        resolved_url = selfbot.pull_link_from_cache(url)
                                    message_string = message_string.replace(url, resolved_url)

                            if resolved_url not in urls_sent_by_bot:
                                print(f"Sending new message to server {server.name}: ")
                                print(f"        {message_string}")
                                if len(message['attachments']) > 0:
                                    message_string = message_string + '\n' + message['attachments'][0]['url']
                                await channel.send(message_string)
                            # Send a new message containing that content

        await asyncio.sleep(random.randint(1, 3))


# Run Bot
client.loop.create_task(update_site())
client.run(TOKEN)
