#import sys
#sys.path.append("D:/DSPLabs/telegram-bot")

import telebot
import parser
from sqlite_db import DB



# Инициируем БД (создается при отсутствии)
#tmp='D:/DSPLabs/telegram-bot/'
db=DB('db.db')
db.creat_table('Telega','id INTEGER PRIMARY KEY, uid TEXT NOT NULL, audio BLOB NOT NULL, imgface BLOB')




TOKEN = "1090552842:AAGchKO-zHMRtVYj09QuuQwBVLC-glrEuAg"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет, когда я вырасту, я буду парсить заголовки с Хабра')

@bot.message_handler(content_types=['photo'])
def text_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Это фото')





need_extension = ['mp3', 'm4a','wav'] #Сюда ввести нужные расширения
@bot.message_handler(content_types=['document']) #Хендлер
def test(message):
  extension = message.document.file_name[-3:] #Определения расширения файла
  if extension in need_extension and message.document.file_size // 1024 // 1024 < 20: #Если такое расширение нужно и вес файла < 20 mb
       bot.send_message(chat_id, 'Это аудио')         






bot.polling()