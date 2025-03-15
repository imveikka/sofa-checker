import os
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
    response = """Töttöröö! This is a Lateksii SofaChecker.
    
See if there's free seats left in the guild room!

Use /count to see the current availability.
"""
    bot.reply_to(message, response)

@bot.message_handler(func=lambda msg: True, commands=['count'])
def send_count(message):
    count = data['headcount']
    if count == 0:
        response = "There's no one in the guild room right now!"
    elif count < 2:
        response = "There's only one person in the guild room!"
    elif count < 5:
        response = f"There's {count} persons in the guild room, join the party!"
    elif count < 11:
        response = f"There's {count} persons in the guild room. Be fast, before you have to sit on someone's lap!"
    else:
        response = f"There's {count} persons in the guild room!! This has to be illegal..."
    response  = response + '\n\n' + 'If you wan\'t to verify, type /view for an image!'
    bot.reply_to(message, response)

@bot.message_handler(func=lambda msg: True, commands=['view'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_photo(chat_id, photo=data['image_box'])
    
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

thread = Thread(target=detection_loop)
thread.start()

bot.infinity_polling()

