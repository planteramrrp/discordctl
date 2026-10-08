# Install
## Dependencies
### Python
- `discord.py-self` (discord interfacing)
- `beautifulsoup4` (scraping og:image og:video)
- `Pillow` (sending images)
- `requests` (scraping og:image og:video)
- `prompt_toolkit` (CLI)
### Programs
- `timg` (rendering images videos)
- any sixel/kitty protocol supporting terminal emulator
### Instructions
- set `TOKEN` env var to discord token
- run `./discordctl`
# Usage
- `ls` list channels and servers
- `cd [n]` go to channels and servers by indexed number
- `cd 0` go back
- `; message content` send message (note space is necessary and any message content is necessary removing it is an unsolved computer science problem)
- `"reply content" ; message content` send replies
- `open [user handle]` open dm
- `clear` clear
- `exit` exit
