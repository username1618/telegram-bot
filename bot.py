import os
import sys
sys.path.append("D:/DSPLabs/telegram-bot/dsptelebot")

import telebot
from telebot import apihelper

import cv2
import tensorflow as tf

import subprocess
import requests
import uuid
import time
import tempfile

from sqlite_db import DB

  
import numpy as np
import align.detect_face as detect_face



# Debug
os.chdir("D:/DSPLabs/telegram-bot/dsptelebot")   





def TelegramAuth(use_proxy=False):
    bot = telebot.TeleBot(TOKEN)
    if use_proxy:
        if 'socks' in proxy_type:
            apihelper.proxy={'http':  proxy_type+'://'+proxy_login+':'+proxy_passw+'@'+proxy_ip+':'+proxy_port,
                               'https': proxy_type+'://'+proxy_login+':'+proxy_passw+'@'+proxy_ip+':'+proxy_port} 
        else:
            apihelper.proxy={proxy_type: proxy_type+'://'+proxy_login+':'+proxy_passw+'@'+proxy_ip+':'+proxy_port}  
    return bot



def getWindowspath(string):
    return string.replace('\\','/')

def getExtension(string):
    return string.split(".")[-1]


def getRndFileNamePath(folder,ext):
    return os.path.join(folder,str("{0}.{1}".format(time.strftime("%Y%m%d-%H%M%S")+'_'+str(uuid.uuid1()), ext)))


def getProxyRequestContent(link):
      session = requests.session()
      if 'socks' in proxy_type:
          session.proxies={'http':  proxy_type+'://'+proxy_login+':'+proxy_passw+'@'+proxy_ip+':'+proxy_port,
                           'https': proxy_type+'://'+proxy_login+':'+proxy_passw+'@'+proxy_ip+':'+proxy_port} 
      else:
          session.proxies={proxy_type: proxy_type+'://'+proxy_login+':'+proxy_passw+'@'+proxy_ip+':'+proxy_port}           
      return session.get(link)


def save_to_pcm16b16000r(in_filename=None, in_bytes=None,out_filename=None): #, returnBinary=False
    with tempfile.TemporaryFile() as temp_out_file:
        temp_in_file = None
        if in_bytes:
            temp_in_file = tempfile.NamedTemporaryFile(delete=False)
            temp_in_file.write(in_bytes)
            in_filename = temp_in_file.name
            temp_in_file.close()
        if not in_filename:
            raise Exception('Neither input file name nor input bytes is specified.')
        
        # Запрос в командную строку для обращения к FFmpeg
        command = [
            r'ffmpeg',  # путь до ffmpeg.exe
            '-i', in_filename,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '2',
            out_filename
        ]

        proc = subprocess.Popen(command, stdout=temp_out_file, stderr=subprocess.DEVNULL)
        proc.wait()

        if temp_in_file:
            os.remove(in_filename)


def FaceDetector_count(**kwargs):

    pnet =           kwargs['pnet']
    rnet =           kwargs['rnet']
    onet =           kwargs['onet']
    factor =         kwargs['factor']
    minsize =        kwargs['minsize']
    threshold =      kwargs['threshold']
    r_g_b_frame =    kwargs['r_g_b_frame']
    face_score_threshold = kwargs['face_score_threshold']

    
    faces, points = detect_face.detect_face(r_g_b_frame, minsize,
                                            pnet, rnet, onet, threshold,
                                            factor)
    result=0
    face_sums = faces.shape[0]
    if face_sums > 0:
       for i, item in enumerate(faces):
           score = round(faces[i, 4], 6)
           print(score)
           if score > face_score_threshold: # порог определения принадлежности объекта к классу "лицо"
              result=result+1
              
    return result






current_dir = getWindowspath(os.getcwd())


TOKEN = ""


# Прокси
proxy_type ='socks5'
proxy_ip   ='213.166.94.35'
proxy_port ='50294'
proxy_login='nMLUMF7vbT'
proxy_passw='mksLLuAuGN'
  
 
# Параметры face recognition
minsize=32
factor=0.7
face_score_threshold=0.65
threshold = [0.4, 0.5, 0.6]
    


# Инициируем БД (создается при отсутствии)
db=DB(os.path.join(current_dir,'Telebot.db'))
db.creat_table('Audio','id INTEGER PRIMARY KEY autoincrement , uid TEXT NOT NULL, audio BLOB')
db.creat_table('Photo','id INTEGER PRIMARY KEY autoincrement , uid TEXT NOT NULL, photo BLOB')



# Авторизация в Telegram
bot = TelegramAuth(use_proxy=True)
    






@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Это тестовый бот. Бот сохраняет аудиосообщения из диалогов в базу данных SQLite. Также бот сохраняет в базу данных фотографии с лицами.')



@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    try:
        chat_id = message.chat.id
        
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
      
        downloaded_file = bot.download_file(file_info.file_path)

        path_to_save=os.path.join(current_dir,file_info.file_path)
        with open(path_to_save, 'wb') as new_file:
           new_file.write(downloaded_file)
        
        
#        if detectFace(path_to_save):
#            db.insertBLOB('Photo','photo',chat_id, path_to_save)
#            bot.send_message(chat_id, "Обнаружено лицо! Фото добавлено в базу данных SQLite. \nИдентификатор пользователя: "+str(chat_id))
#        else:
#            bot.send_message(chat_id, "Лицо не обнаружено.")
        
        
        r_g_b_frame = cv2.imread(path_to_save,1)
        faces_count = FaceDetector_count(
                                         r_g_b_frame = r_g_b_frame,
                                         minsize=minsize, threshold=threshold, factor=factor,
                                         pnet = pnet, rnet = rnet, onet = onet, 
                                         face_score_threshold = face_score_threshold,
                                         )
        if faces_count>0:
            bot.reply_to(message,'Обнаружено лиц:'+str(faces_count)+'\nФото добавлено в базу данных SQLite.\nИдентификатор пользователя: '+str(chat_id) )
        else:
            bot.reply_to(message,'Лицо не обнаружено.')
        
        
        os.remove(path_to_save)
    except Exception as e:
        bot.reply_to(message,e )




need_extension = ['jpg', 'jpeg','png','bmp','tiff','gif','raw','jp2'] 
@bot.message_handler(content_types=['document']) 
def handle_docs_photo(message):

    try:    
      chat_id = message.chat.id
      file_info = bot.get_file(message.document.file_id)
      extension = getExtension(message.document.file_name)
      
      if extension in need_extension: 
          bot.send_message(chat_id,'Добавлен документ с изображением' )
    
          file = getProxyRequestContent('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
       
       
          if file.status_code == 200:
                path_to_save=getRndFileNamePath(current_dir, extension)

                with open(path_to_save, 'wb') as new_file:
                   new_file.write(file.content)
                
            
                r_g_b_frame = cv2.imread(path_to_save,1)
                faces_count = FaceDetector_count(
                                                 r_g_b_frame = r_g_b_frame,
                                                 minsize=minsize, threshold=threshold, factor=factor,
                                                 pnet = pnet, rnet = rnet, onet = onet, 
                                                 face_score_threshold = face_score_threshold,
                                                 )
                if faces_count>0:
                    db.insertBLOB('Photo','photo',chat_id, path_to_save)
                    bot.reply_to(message,'Обнаружено лиц:'+str(faces_count)+'\nФото добавлено в базу данных SQLite.\nИдентификатор пользователя: '+str(chat_id) )
                else:
                    bot.reply_to(message,'Лицо не обнаружено.')
        
                os.remove(path_to_save)
    except Exception as e:
        bot.reply_to(message,e )
     






@bot.message_handler(content_types=['audio']) 
def handle_audio(message):
    try:
      chat_id = message.chat.id
      file_info = bot.get_file(message.audio.file_id)
      extension = getExtension(file_info.file_path) #os.path.splitext(file_info.file_path)[1][1:]


      file = getProxyRequestContent('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
   
   
      if file.status_code == 200:
            path_to_save=getRndFileNamePath(current_dir,'wav')
            try:
                save_to_pcm16b16000r(in_bytes = file.content,
                                     out_filename = path_to_save) 
            except Exception as e:
                bot.send_message(chat_id,'Error while converting file to wav. Will save as is.\nError'+e )   
                with open(getRndFileNamePath(current_dir, extension), 'wb') as f:
                    f.write(file.content)
                    
         
            db.insertBLOB('Audio','audio',chat_id, path_to_save)
            os.remove(path_to_save)
            
            bot.send_message(chat_id, "Аудио добавлено в базу данных SQLite. \nИдентификатор пользователя: "+str(chat_id))
      else:
            bot.send_message(chat_id, "Audiofile.status_code = "+str(file.status_code))
            
    except Exception as e:
        bot.send_message(chat_id,e )





@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        chat_id = message.chat.id
        file_info = bot.get_file(message.voice.file_id)

        file = getProxyRequestContent('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        
        if file.status_code == 200:
            path_to_save=getRndFileNamePath(current_dir, 'wav')
            try:
                save_to_pcm16b16000r(in_bytes = file.content,
                                     out_filename = path_to_save)
            except Exception as e:
                bot.send_message(chat_id,'Error while converting voice to wav. Will save as is.\nError:'+e )   
                with open(getRndFileNamePath(current_dir, 'ogg'), 'wb') as f:
                    f.write(file.content)
                
            
            db.insertBLOB('Audio','audio',chat_id, path_to_save)
            os.remove(path_to_save)
        else:
            bot.send_message(chat_id, "Voice.status_code = "+str(file.status_code))
 
        bot.send_message(chat_id, "Голосовое сообщение добавлено в базу данных SQLite. \nИдентификатор пользователя: "+str(chat_id))
    except Exception as e:
        bot.send_message(chat_id,e )







if __name__ == '__main__':
    
    # Создаем сессию в tf для распознавания лиц на фото
    with tf.Graph().as_default():
        with tf.Session(config=tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True),
                                          log_device_placement=False)) as sess:
            pnet, rnet, onet = detect_face.create_mtcnn(sess, os.path.join(os.getcwd(), "align"))


    
            bot.polling() # запускаем бота
    
    
    
    
    
    
    
    
