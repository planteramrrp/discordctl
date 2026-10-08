import discord
from bs4 import BeautifulSoup
from PIL import ImageGrab
import io
import re
import requests
import asyncio
import threading
import textwrap
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout 
from prompt_toolkit.formatted_text import ANSI
import subprocess

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
	servers = await client.fetch_guilds()
	servers = ["DM"] + servers
	print("hi hello logged in as", client.user.name)

def ogimage(url):
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"} 

	response = requests.get(url, headers=headers, timeout=10)
	soup = BeautifulSoup(response.text, "html.parser") 
	image = soup.find("meta", property="og:image")
	if image and image.get("content"): 
		return image["content"] 
	return None

def ogvideo(url):
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
	response = requests.get(url, headers=headers, timeout=10)
	soup = BeautifulSoup(response.text, "html.parser") 
	video = soup.find("meta", property="og:video")
	if video and video.get("content"): 
		return video["content"] 
	return None

async def render_message(message):
	authoruname = message.author.name
	# authordname = message.author.display_name
	# r = message.author.color.r
	# g = message.author.color.g
	# b = message.author.color.b
	content = message.content
	# datetime = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
	if message.embeds:
		for e in message.embeds:
			url = e.url
			ogimageurl = ogimage(url)
			if ogimageurl:
				url = ogimageurl
			else:
				ogvideourl = ogvideo(url)
				if ogvideourl:
					url = ogvideourl
			try:
				subprocess.run(["timg", url])
			except:
				pass
	if message.attachments:
		for a in message.attachments:
			url = a.url
			try:
				subprocess.run(["timg", url])
			except:
				pass
	
	if message.reference:
		reply = await channel.fetch_message(message.reference.message_id)
		print(f'[ {reply.author.name}: {reply.content} ]')
	print(f'{authoruname}: {content}')	

async def get_history(chan, num):
	return [message async for message in chan.history(limit=num)]

@client.event
async def on_message(message):
	global channel
	guild = message.guild
	if message.channel == channel:
		try:
			await render_message(message)
		except:
			pass		

def input_loop():
	global servers
	global channels
	global server
	global channel
	attachments = []
	
	session = PromptSession()
	with patch_stdout():
		while True:
			future = asyncio.run_coroutine_threadsafe(session.prompt_async(ANSI(f'\x1b[0;32mdiscordctl\x1b[0m:\x1b[0;32m/{server if server else ""}{"/" if server else ""}{(channel if isinstance(channel, discord.TextChannel) else channel.recipient.name) if channel else ""}\x1b[0m$ ')), client.loop)
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
								print(f'{index} {i.recipient.name}')	
					else:
						print("0 ..")
						for index, i in enumerate(channels):
							if index > 0:
								print(f'{index} {i.name}')	
			if msg.split()[0] == "cd":
				target = msg.split()[1]	
				for i in target.split("/"):
					try:
						if not server:
							if int(i) == 0 or i == "..":
								server = "DM"
								future = asyncio.run_coroutine_threadsafe(client.fetch_private_channels(), client.loop)
								result = future.result()
								channels = [".."] + result
							else:
								i = int(i)
								server = servers[i]
								future = asyncio.run_coroutine_threadsafe(client.fetch_guild(server.id), client.loop)
								result = future.result()
								future = asyncio.run_coroutine_threadsafe(result.fetch_channels(), client.loop)
								result = future.result()
								channels = [".."] + result
						else:
							if int(i) == 0 or i == "..":
								if channel:
									channel = None
								else:
									server = None
							else:
								i = int(i)
								channel = channels[i]
					except:
						pass

			if msg.split(maxsplit=1)[0] == ";":
				split = msg.split(maxsplit=1)
				content = split[1] if len(split) > 1 else "ㅤ"
				if isinstance(channel, discord.TextChannel):
					future = asyncio.run_coroutine_threadsafe(channel.send(content, files=attachments), client.loop)
					result = future.result()
					attachments = []
				if isinstance(channel, discord.DMChannel):
					future = asyncio.run_coroutine_threadsafe(channel.send(content, files=attachments), client.loop)
					result = future.result()
					attachments = []
			if msg.split()[0] == "history" and channel:
				amount = int(msg.split()[1]) if len(msg.split())-1 else 100 
				future = asyncio.run_coroutine_threadsafe(get_history(channel, amount), client.loop)
				result = future.result()
				history = result 
				for i in history[::-1]:
					future = asyncio.run_coroutine_threadsafe(render_message(i), client.loop)
					result = future.result()
			repmatch = re.match(r'"(.+)"\s*;\s*(.*)', msg)
			if repmatch:
				reply = repmatch.group(1)
				content = repmatch.group(2)
				found = False
				amount = 50
				while not found:
					amount = amount *2
					future = asyncio.run_coroutine_threadsafe(get_history(channel, amount), client.loop)
					result = future.result()
					history = result
					for i in history:
						if i.content == reply:
							future = asyncio.run_coroutine_threadsafe(i.reply(content, files=attachments), client.loop)
							result = future.result()
							found = True
							break
			if msg.split()[0] == "open":
				target = msg.split()[1]
				future = asyncio.run_coroutine_threadsafe(client.fetch_guild(server.id), client.loop)
				result = future.result()
				future = asyncio.run_coroutine_threadsafe(result.query_members(target), client.loop)
				result = future.result()[0]
				# for u in result:
					# if u.global_name == target:
						# result = u
				try:
					future = asyncio.run_coroutine_threadsafe(result.create_dm(), client.loop)
					result = future.result()
				except:
					pass
			if msg.split()[0] == "clear":
				subprocess.run(["clear"])
			if msg == "+":
				img = ImageGrab.grabclipboard()
				if img:
					bytes_io = io.BytesIO()
					img.save(bytes_io, format="PNG")
					bytes_io.seek(0)
					attachments.append(discord.File(fp=bytes_io, filename="clip.png"))

			if msg == "exit":
				future = asyncio.run_coroutine_threadsafe(client.close(), client.loop)
				result = future.result()
				break

loop = threading.Thread(target=input_loop)
loop.start()
client.run(token)
	
