import time
import subprocess
import telepot
import sys
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space


class MyBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MyBot, self).__init__(*args, **kwargs)
        self.command = False
        self.get = False
        self.first = True
        self.USER = sys.argv[1]
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
                elif self.get:
                    self.get_file(text, chat_id)
                elif self.command:
                    self.exec_command(text, chat_id)
                else:
                    bot.sendMessage(chat_id, "I'm waiting instructions!! :)")
            elif content_type in self.types:
                self.save(msg[content_type], chat_id)
            else:
                bot.sendMessage(chat_id, "I can't work with this information type, I'm sorry.")

    def exec_command(self, command, chat):
        args = command.split(" ")
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        out = "No output" if out == "" else "\n" + out
        err = "No errors" if err == "" else err
        bot.sendMessage(chat, "`Error: {}\nOutput: {}`".format(err, out), parse_mode="Markdown")
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


