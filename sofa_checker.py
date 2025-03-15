import telebot
import time
from threading import Thread
from PIL import Image
from ultralytics import YOLO
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.v2.functional import pil_to_tensor, to_pil_image
import imageio
from getpass import getpass

BOT_TOKEN = getpass('token: ')

bot = telebot.TeleBot(BOT_TOKEN)

data = {
    "image_raw": None,
    "image_box": None,
    "headcount": 0,
}

model = YOLO('./best.pt', verbose=False)


@bot.message_handler(func=lambda msg: True, commands=['start', 'hello'])
def send_welcome(message):
    response = """Töttöröö! This is a Lateksii SofaChecker-bot 🔥🤖.
    
See if there's free seats left in the guild room sofa zone 🛋!

Use /status to see the current availability, /help to list all commands 📋.
"""
    bot.reply_to(message, response)


@bot.message_handler(func=lambda msg: True, commands=['status'])
def send_status(message):
    count = data['headcount']
    if count == 0:
        response = "The sofa zone seems to be empty! Greate chance to take a nap... 😴"
    elif count < 6:
        response = "I see some movement, but still there's plenty of room! 🤓"
    elif count < 10:
        response = "The sofa zone is filling up! Be fast, before you have to sit on someone's lap! 😱"
    elif count < 12:
        response = f"The sofa zone room is full. But don't worry, there's always room for one! 😉"
    else:
        response = f"There's a mayhem going on, better call the police! 👮"
    response  = response + '\n\n' + 'Don\'t believe me? Type /view for an image! 🧐'
    bot.reply_to(message, response)


@bot.message_handler(func=lambda msg: True, commands=['count'])
def send_count(message):
    count = data['headcount']
    if count == 0:
        response = "There's no one in the sofa zone. ❌"
    elif count == 1:
        response = "I see only one person there. Go keep company! 🤗"
    else:
        response = f"I see {count} persons! 🙌"
    bot.reply_to(message, response)


@bot.message_handler(func=lambda msg: True, commands=['view'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_photo(chat_id, photo=data['image_box'])


@bot.message_handler(func=lambda msg: True, commands=['help'])
def send_help(message):
    response = """Here's my vocabulary: 💬
/start
/hello
/status
/view
/count
/help"""
    bot.reply_to(message, response)


@bot.message_handler(func=lambda msg: True)
def send_unknown(message):
    bot.reply_to(message, "Not found in my vocabulary! 😵 Use /help to see all the commands! 📋")
    

def detection_loop():
    while True:
        get_image()
        results = model.predict(data['image_raw'], conf=.3)[0]
        data['headcount'] = len(results.boxes.cls)
        boxes = results.boxes.xyxy
        image_tensor = pil_to_tensor(data['image_raw'])
        image = draw_bounding_boxes(image_tensor, boxes, 
                                    colors='red', width=5)
        data['image_box'] = to_pil_image(image)
        time.sleep(60)
    

def get_image():
    reader = imageio.get_reader('<video0>')
    img = reader.get_data(0)
    reader.close()
    data['image_raw'] = Image.fromarray(img)
    

if __name__ == '__main__':

    thread = Thread(target=detection_loop)
    thread.start()
    
    bot.infinity_polling()

