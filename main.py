import discord
import os
import asyncio
import random
import selfbot
import link_resolver
from urlextract import URLExtract
from sys import argv

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
            for channel in server.channels:
                if channel.name == '💾│packs' and server.name == "BotTesting":
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
                        parsed_message = parse_message(message)

                        message_data = parse_urls(parsed_message, message)

                        if message_data:
                            parsed_message = message_data[0]
                            resolved_url = message_data[1]

                            await send_message_to_discord(resolved_url,
                                                          parsed_message,
                                                          message,
                                                          urls_sent_by_bot,
                                                          server,
                                                          channel)
                        else:
                            print('message urls could not be resolved')

                        """
                        print("<-----Checking for skipped urls in cache----->")
                        await check_skipped_urls(channel, urls_sent_by_bot)
                        """

        await asyncio.sleep(random.randint(1, 3))


def parse_message(msg):
    message_string = msg['content']
    try:
        message_string = message_string.replace('@everyone', '')
    except:
        print('message did not contain @everyone')

    try:
        message_string = message_string.replace('join our groups for more : ', '')
    except:
        print('message did not have a group ad')

    return message_string


def parse_urls(msg, server_message):
    urls = ex.find_urls(msg)
    resolved = False
    for url in urls:
        if 'pastelink' in url:
            msg = msg.replace(url, '')
        if 'bit.ly' in url:
            print(f"Resolving url: {url}")

            resolved = resolve_bitly_url(url, server_message)
            if resolved:
                msg = msg.replace(url, resolved)

    if not resolved:
        return False

    return msg, resolved


def resolve_bitly_url(url, server_message):
    cache = selfbot.pull_link_from_cache(url)
    if cache:
        if cache == 'cannot resolve':
            return False
        return cache

    image = None
    if len(server_message['attachments']) > 0:
        image = server_message['attachments'][0]['url']

    res = link_resolver.resolve_link(url)
    if res:
        selfbot.add_link_to_cache(url, res, image=image, message=server_message['content'])
        return res

    selfbot.add_link_to_cache(url, 'cannot resolve')
    return False


async def check_skipped_urls(current_channel, urls_sent_by_bot, include_unresolved=False):
    cache_list = selfbot.pull_all_data_from_cache()

    messages_to_send = []

    """
    for entry in cache_list:
        if 'post_cache_without_image' not in argv:
            if entry['resolved'] != 'cannot resolve' and 'image' in list(entry.keys()) and \
               entry['resolved'] not in urls_sent_by_bot:

                if 'message' in list(entry.keys()):
                    message = f"{entry['message']}" + '\n'  \
                              f"{entry['resolved']}" + "\n" \
                              f"{entry['image']}"
                else:
                    message = f"{entry['resolved']}" + "\n" \
                              f"{entry['image']}"

                print("Appending to skipped messages...")
                messages_to_send.append(message)
        else:
            if entry['resolved'] != 'cannot resolve' and entry['resolved'] not in urls_sent_by_bot:
                print("Posting entry with no image")
                if 'message' in list(entry.keys()) and 'image' in list(entry.keys()):
                    message = f"{entry['message']}" + '\n' \
                              f"{entry['resolved']}" + "\n" \
                              f"{entry['image']}"
                elif 'message' in list(entry.keys()):
                    message = f"{entry['message']}" + '\n' \
                              f"{entry['resolved']}"
                else:
                    message = f"{entry['resolved']}"

                print("Appending to skipped messages...")
                messages_to_send.append(message)

    print(f"Sending Messages: {messages_to_send}")
    for msg in messages_to_send:
        await current_channel.send(msg)
        print("Message sent...")
    """


async def send_message_to_discord(resolved_url, user_message, server_message, urls_sent_by_bot, server, channel):
    if resolved_url not in urls_sent_by_bot:
        print(f"Sending new message to server {server.name}: ")
        print(f"        {user_message}")
        if len(server_message['attachments']) > 0:
            message_string = user_message + '\n' + server_message['attachments'][0]['url']
        await channel.send(message_string)

# Run Bot
client.loop.create_task(update_site())
client.run(TOKEN)
