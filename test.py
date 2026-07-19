#!/bin/python

import discord
import asyncio
import threading
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout 
from prompt_toolkit.formatted_text import ANSI

client = discord.Client()
token = os.environ['TOKEN']

servers = []
channels = []

server = None 
channel = None 

ready = False

@client.event
async def on_ready():
	global servers
	print("hi hello logged in as ", client.user)
	servers = await client.fetch_guilds()
	servers = ["DM"] + servers

def render_message(message):
	authoruname = message.author
	authordname = message.author.display_name
	# r = message.author.color.r
	# g = message.author.color.g
	# b = message.author.color.b
	content = message.content
	# datetime = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
	
	print(f'{authordname}: {content}')	

async def get_history(chan, num):
	return [message async for message in chan.history(limit=num)]

@client.event
async def on_message(message):
	global channel
	guild = message.guild
	if message.channel == channel:
		try:
			authoruname = message.author
			authordname = message.author.display_name
			print(f"{message.author.display_name}: {message.content}")
		except:
			pass		

def input_loop():
	global servers
	global channels
	global server
	global channel
	
	session = PromptSession()
	with patch_stdout():
		while True:
			future = asyncio.run_coroutine_threadsafe(session.prompt_async(ANSI(f'\x1b[0;32mdiscordctl\x1b[0m:\x1b[0;32m/{server if server else ""}{"/" if server else ""}{(channel if isinstance(channel, discord.TextChannel) else channel.recipient.display_name.split(maxsplit=3)[-1]) if channel else ""}\x1b[0m$ ')), client.loop)
			result = future.result()
			msg = result 
			if msg == "ls" and not channel:
				if not server:
					for index, i in enumerate(servers):
						print(f'{index} {i}')
				else:
					if server == "DM":
						print("0 ..")
						for index, i in enumerate(channels):
							if index > 0:
								print(f'{index} {i.recipient.global_name}')	
					else:
						print("0 ..")
						for index, i in enumerate(channels):
							if index > 0:
								print(f'{index} {i.name}')	
			if msg.split()[0] == "cd":
				target = int(msg.split()[1])	
				if not server:
					if target == 0:
						server = "DM"
						future = asyncio.run_coroutine_threadsafe(client.fetch_private_channels(), client.loop)
						result = future.result()
						channels = [".."] + result
					else:
						server = servers[target]
						future = asyncio.run_coroutine_threadsafe(client.fetch_guild(server.id), client.loop)
						result = future.result()
						future = asyncio.run_coroutine_threadsafe(result.fetch_channels(), client.loop)
						result = future.result()
						channels = [".."] + result
				else:
					if target == 0:
						if channel:
							channel = None
						else:
							server = None
					else:
						channel = channels[target]
			if msg.split(maxsplit=1)[0] == ";":
				content = msg.split(maxsplit=1)[1]
				if isinstance(channel, discord.TextChannel):
					future = asyncio.run_coroutine_threadsafe(channel.send(content), client.loop)
					result = future.result()
				if isinstance(channel, discord.DMChannel):
					future = asyncio.run_coroutine_threadsafe(channel.send(content), client.loop)
					result = future.result()
			if msg.split()[0] == "history" and channel:
				amount = int(msg.split()[1]) if len(msg.split())-1 else 100 
				future = asyncio.run_coroutine_threadsafe(get_history(channel, amount), client.loop)
				result = future.result()
				history = result 
				for i in history[::-1]:
					render_message(i)
			if msg == "exit":
				future = asyncio.run_coroutine_threadsafe(client.close(), client.loop)
				result = future.result()
				break 

loop = threading.Thread(target=input_loop)
loop.start()
client.run(token)
	
