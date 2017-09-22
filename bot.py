import time
import subprocess
import telepot
import sys
import os
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space


class MyBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MyBot, self).__init__(*args, **kwargs)
        self.command = False
        self.get = False
        self.cd = False
        self.python = False
        self.torrent = False
        self.t_torrent = None
        self.rtorrent = False
        self.USER = sys.argv[1]
        self.TIMEOUT = 60
        self.DOWNLOAD = sys.argv[3] if sys.argv[3][-1] == '/' else sys.argv[3] + "/"
        self.types = ["audio", "document", "photo", "video", "voice", "video_note"]

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == "text":
            print("Received message from {}: {}".format(msg['from']['username'], msg['text']))
        else:
            print("Received message from {} and it is a {}".format(msg['from']['username'], content_type))

        if msg['from']['username'] != self.USER and chat_type == "private":
            bot.sendMessage(chat_id, "You don't have authorization to talk with me. :(")
        else:
            if content_type == "text":
                text = msg['text']
                if text == "/command":
                    self.command = True
                    bot.sendMessage(chat_id, "What can I do for you?")
                elif text == "/get":
                    self.get = True
                    bot.sendMessage(chat_id, "What file you want?")
                elif text == "/cd":
                    self.cd = True
                    bot.sendMessage(chat_id, "You are in `{}`\nTo where you want to go?".format(os.getcwd()),
                                    parse_mode="Markdown")
                elif text == "/python":
                    self.python = True
                    bot.sendMessage(chat_id, "Send-me the expression!")
                elif text == "/torrent":
                    self.torrent = True
                    bot.sendMessage(chat_id, "Send-me the magnet!")
                elif text == "/ltorrent":
                    self.list_torrent(chat_id)
                elif text == "/rtorrent":
                    self.rtorrent = True
                    bot.sendMessage(chat_id, "Send-me the torrent id that you want remove")
                elif self.get:
                    self.get_file(text, chat_id)
                elif self.command:
                    self.exec_command(text, chat_id)
                elif self.cd:
                    self.change_wd(text, chat_id)
                elif self.python:
                    self.python_eval(text, chat_id)
                elif self.torrent:
                    self.add_torrent(text, chat_id)
                elif self.rtorrent:
                    self.rem_torrent(text, chat_id)
                else:
                    bot.sendMessage(chat_id, "I'm waiting instructions!! :)")
            elif content_type in self.types:
                self.save(msg[content_type], chat_id)
            else:
                bot.sendMessage(chat_id, "I can't work with this information type, I'm sorry.")

    def exec_command(self, command, chat):
        args = command.split(" ")
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        try:
            out, err = process.communicate(input=subprocess.DEVNULL, timeout=self.TIMEOUT)
            out = out.decode('utf-8')
            err = err.decode('utf-8')
            out = "No output" if out == "" else "\n" + out
            err = "No errors" if err == "" else err
            bot.sendMessage(chat, "`Error: {}\nOutput: {}`".format(err, out), parse_mode="Markdown")
        except Exception as e:
            bot.sendMessage(chat, "`An error was occurred:\n{}`".format(e), parse_mode="Markdown")
        self.command = False

    def get_file(self, path, chat):
        f = open(path, "rb")
        bot.sendDocument(chat, f)
        self.get = False

    def save(self, file, chat):
        if type(file) == list:
            file = file[-1]
        f = bot.getFile(file['file_id'])
        url = "https://api.telegram.org/file/bot" + sys.argv[2] + "/" + f['file_path']
        if 'file_name' in file:
            name = file['file_name']
        else:
            name = str(int(time.time()))
        self.exec_command("wget -q -O " + self.DOWNLOAD + name + " " + url, chat)
        if file['mime_type'] == "application/x-bittorrent":
            bot.sendMessage(chat, "Want start download? [y/n]")
            self.torrent = True
            self.t_torrent = self.DOWNLOAD + name

    def change_wd(self, path, chat):
        try:
            os.chdir(path)
            bot.sendMessage(chat, "Actual path is: `{}`".format(os.getcwd()), parse_mode="Markdown")
        except Exception as e:
            bot.sendMessage(chat, "`An error was occurred:\n{}`".format(e), parse_mode="Markdown")
        self.cd = False

    def python_eval(self, expr, chat):
        try:
            r = eval(expr)
            bot.sendMessage(chat, "`{}`".format(r), parse_mode="Markdown")
        except Exception as e:
            bot.sendMessage(chat, "`An error was occurred:\n{}`".format(e), parse_mode="Markdown")
        self.python = False

    @staticmethod
    def check_transmission():
        process = subprocess.Popen(["ps -eaf | grep transmission-daemon"], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, shell=True)
        out, err = process.communicate()
        out = out.decode('utf-8').split("\n")
        is_running = False
        for i in out:
            if "grep" not in i and i != "":
                is_running = True
        return is_running

    def start_torrent(self):
        if not self.check_transmission():
            subprocess.Popen("transmission-daemon")

    def add_torrent(self, text, chat):
        self.start_torrent()
        if text == "y" or "magnet" in text:
            torrent = self.t_torrent if self.t_torrent is not None and text == "y" else text
            self.exec_command("transmission-remote --add " + torrent, chat)
        elif text == "n":
            bot.sendMessage(chat, "Okay")
        else:
            bot.sendMessage(chat, "Invalid option")
        self.torrent = False
        self.t_torrent = None

    def list_torrent(self, chat):
        self.start_torrent()
        self.exec_command("transmission-remote -l", chat)

    def rem_torrent(self, text, chat):
        self.start_torrent()
        self.exec_command("transmission-remote -t {} -r".format(text), chat)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Incorrect usage")
        print("Try `python {} ALLOWED_USER BOT_TOKEN PATH_DOWNLOADS`".format(sys.argv[0]))
        sys.exit(-1)
    bot = telepot.DelegatorBot(sys.argv[2], [
        pave_event_space()(
            per_chat_id(), create_open, MyBot, timeout=60),
    ])
    MessageLoop(bot).run_as_thread()
    print("Listening...")
    while True:
        time.sleep(10)
