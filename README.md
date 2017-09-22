# telebot

## Just a telegram bot.

## Features:
  - Save files for you
  - Send files to you
  - Add torrents to be downloaded
  - Evaluate python expressions
  - Run commands on your computer
  
## Requirements:
  - python3+
  - telepot
  - pip*
  - virtualenv*
  - screen/tmux*
  - transmission-daemon(for download torrents)
  - transmission-remote(for download torrents)

*optional

## How to install:
```bash
$ git clone https://github.com/washingt0/telebot.git
$ cd telebot
$ virtualenv -p python3 env
$ source env/bin/activate
$ (env) pip install -r requirements.txt
$ (env) deactivate
```

## How to use:
```bash
$ (env) python telebot.py USERNAME TOKEN PATH
```
`USERNAME` = Telegram's username of who is authorized to interact with bot.

`TOKEN` = Token given by BotFather.

`PATH` = Path of an folder to store all downloaded files.

## Compatibility
GNU/Linux systems.
