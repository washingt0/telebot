import telepot
from telepot.loop import MessageLoop
import time
import subprocess

command = False
get = False

def handle(msg):
    global command, get
    rem = msg['from']
    chat = msg['chat']
    text = msg['text']
    print("Received message from {}: {}".format(rem['username'], text))
    if rem['username'] != "YOUR_USERNAME" and chat['username'] != "YOUR_USERNAME":
        bot.sendPhoto(chat['id'], "https://http.cat/403")
    else:
        if text == "/command":
            command = True
            bot.sendMessage(chat['id'], "How can I do for you?")
        elif text == "/get":
            get = True
            bot.sendMessage(chat['id'], "What file you want?")
        elif get:
            f = open(text, "rb")
            bot.sendDocument(chat['id'], f)
            get = False
        elif command:
            args = text.split(" ")
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            bot.sendMessage(chat['id'], "`Error: {}\nOutput: \n{}`".format(err.decode('utf-8'), out.decode('utf-8')), parse_mode="Markdown")
            command = False


bot = telepot.Bot("TOKEN")

MessageLoop(bot, handle).run_as_thread()

print("Listening...")

while True:
    time.sleep(10)
