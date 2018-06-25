#!/usr/bin/python3
import mysql.connector
import json
import mimetypes
import os
import time
import urllib.request
import pyperclip
import pyautogui
import pyscreenshot
import pytesseract
import requests
import difflib
import requests
import sqlite3
from PIL import ImageChops
from datetime import datetime
import subprocess
import random

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By


os.chdir('/home/wasap/whatsapp-bot')
driver = None
DBG = 1
loc = 3

##########
# El ZOOM de la pagina esa en 125%
##########
pyautogui.FAILSAFE = True
url_img = 'http://www.benteveo.com/siguit-inmo/images/'
image_folder = "/home/wasap/whatsapp-bot/media/"

# COORDENADAS WASAP:
pos_search_contact = (861,322) # Buscar o empezar un chat nuevo
pos_close_search_contact = (1004,320)

pos_tel_1 = (845, 367)  # posicion del mensaje nuevo a la izquierda
pos_tel_2 = (845, 491)  # posicion del mensaje nuevo a la izquierda
pos_tel_3 = (845, 574)  # posicion del mensaje nuevo a la izquierda
pos_tel_4 = (845, 662)  # posicion del mensaje nuevo a la izquierda
pos_tel_5 = (845, 740)  # posicion del mensaje nuevo a la izquierda

tupla_pos_tel = ((845, 367), (845, 491), (845, 574), (845, 662), (845, 740))

pos_tel_1_searched = (854, 468)  # posicion del mensaje nuevo a la izquierda
pos_new_text = (1077, 652)  # El ultimo texto que manda el usuario en la zona de conversacion
pos_bnt_no_es_spam = (1321, 646)  # Posicion del boton de "NO ES SPAM"
pos_res_frame = (1556, 656)
region_tel_1 = (1117, 91, 1308, 125)  # El num de telefono que aparece arriba
region_tel_1_searched = (749, 454, 956, 491)  # El num de telefono que aparece arriba
region_new_text = (1039, 633, 1547, 679)  # Region donde aparece el ultimo texto
region_messages = (660, 361, 1020, 712)  # zona donde estan todos los mensajes recibidos
region_new_contact = (1242, 628, 1385, 660)  # Boton "NO ES SPAM" del cartel de spam
region_res_frame = (1527, 636, 1580, 677)  # Region donde aparece la X para cerrar un cuadro de respuesta


# COORDENADAS FILE MANAGER
pos_folder = (262, 113)  # filemanager
pos_img0 = (262, 113)  # Primer imagen en el filemanager
pos_text_box = (1400, 400)  # caja donde se encuentra la conversacion
# SCROLL ENTRE MENSAJES
scroll_amount = -2.1
scroll_up = 100 #Scrollea por la lista de numeros hasta llegar al principio
###########################################################


def close_spam(pos, posbtnspam, reg):
    """Cierra la pregunta mensaje spam"""
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    if text.upper() == 'NO ES SPAM':
        pyautogui.click(posbtnspam)  # Voy a la posicion 1 y clickeo
###########################################################


def close_res_frame(pos):
    """Cierra la respuesta a un mensaje"""
    if DBG: print('Fn: chkresframe')
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo
    time.sleep(0.2)
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo

###########################################################


def check_for_new_messages_graphical(messagesframezone):
    """Checkea de manera grafica los nuevos mensajes"""
    im1 = pyscreenshot.grab(bbox=messagesframezone)
    time.sleep(3)
    im2 = pyscreenshot.grab(bbox=messagesframezone)
    diff = ImageChops.difference(im1, im2)

    if diff.getbbox():
        return True
    else:
        return False
###########################################################


def read_phone_number(pos, reg):
    """Lee el numero de telefono"""
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo
    time.sleep(0.1)
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    return text.upper()
###########################################################


def read_last_message(pos, reg):
    if DBG == 1: print('Func. Leer Msj')
    # im = pyscreenshot.grab(bbox=reg)

    pyautogui.click(x=pos[0], y=pos[1], clicks=3, interval=0.2)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    text = pyperclip.paste()
    pyperclip.copy('')
    return text.upper()
    # else:
    #     return ''
###########################################################


def archive_chat(pos):
    pyautogui.click(pos, button='right')
    time.sleep(0.3)
    pyautogui.moveRel(100, 40)
    pyautogui.click()
###########################################################


def copy_paste(m):
    if DBG: print('F: Copypaste')
    pyperclip.copy(m)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
###########################################################

def generate_greetings(prop_data):
    response = ''
    if(prop_data['prod_nom']):
        response += f"Si te interesa esta propiedad comunicate con {prop_data['prod_nom']} tel: {prop_data['prod_tel']} \n\n"
    # response += "¿Te interesa otra propiedad? Pasanos el código \n\n"
    return response
###########################################################


def generate_greetings_failed(telephone='1158717399'):
    response = f"Podemos responderte via Whatsapp sobre nuestras propiedades ofertadas. \
    Para cualquier otra consulta te recomiendo comunicarte con la Inmobiliaria al teléfono \
    {telephone} Si querés consultar sobre alguna propiedad en particular, pasanos su código."
    return response
###########################################################


def write_copying(msj, pos, enter=0):
    print(msj)
    # pyautogui.click(pos)
    time.sleep(0.4)
    copy_paste(msj)
    time.sleep(0.1)
    if enter:
        pyautogui.press('enter')
###########################################################


def get_propertys_data():
    with open('%s/schedule.json' % (os.getcwd())) as json_data:
        data = json.load(json_data)
        return data
###########################################################


def get_property_data(data, texto):
    print("Buscando Prop en el texto que ingreso el cliente")

    operation_type = ''
    description = ''
    direction = ''
    price = ''
    code = ''
    prod_nom = ''
    prod_tel = ''
    key = ''
    texto = texto.upper()
    b = ''
    # Debo encontrar un codigo valido
    for i in data['schedule']:
        code = i['Cod']

        if code in texto:
            # if propid == i["reference_code"]:
            if DBG: print('Propiedad encontrada :' + code)
            key = i['key']
            operation_type = i["TipodeOperacion"]
            description = i["Descripcion"]
            direction = i["Direccion"]
            price = i["Precio"]
            prod_nom = i['prod_nom']
            prod_tel = i['prod_tel']

            p = 0
            for image in i['images']:
                image_name = 'T_' + image['url']
                # download_images(url_img + image_name, image_folder + str(p))
                print("Copiando imagenes")
                subprocess.call(["cp", f"{os.getcwd()}/all_media/thumbs/{image_name}", f"{os.getcwd()}/media/{image_name}"])
                p += 1
            break

    return {"key" : key, "code" : code, "operation_type" : operation_type,
            "description" : description, "direction" : direction,
            "price" : price, "prod_nom" : prod_nom, "prod_tel" : prod_tel}
###########################################################


def get_property_images(data, texto, fotodir):
    p = 0
    print("tomando data de fotos")
    for i in data['schedule']:
        codigo = i["Cod"]
        if codigo in texto:
            for entry in i['images']:
                p += 1
                # fotourl = i['photos'][p]['image']
                fotourl = entry['url']
                print(fotourl)
                guardarfoto(url_img + fotourl, fotodir + str(p))
            break
    return p
###########################################################


def check_if_message_was_answered(message, telephone):
    print("DEBUG: check_if_message_was_answered")

    sql_select = '''SELECT id FROM conversations WHERE phone = ? and message = ? and (status = 1 or status = 2 )'''
    cursor.execute(sql_select, (telephone, message))
    try:
        result = cursor.fetchone()[0]
    except TypeError:
        result = 0

    if result >= 1:
        print("DEBUG: message ALREADY responded")
        return 1
    else:
        print("DEBUG: message NOT responded")
        return 0
###########################################################


def get_data_and_response(message, telephone):
    status = 1

    sql_insert = '''INSERT INTO conversations(phone, message, status)
                          VALUES(?,?,?)'''

    sql_select = '''SELECT id FROM conversations WHERE phone = ? and message = ? and status = ?'''

    sql_update = '''UPDATE conversations SET status WHERE id = ?'''

    all_props_data = get_propertys_data()
    prop_data = get_property_data(all_props_data, message)
    print(prop_data)
    if prop_data["code"] and prop_data["operation_type"]:
        print("RESPONSE")
        response = generate_response(prop_data)
        write_copying(response, pos_tel_1, 1)
        print("COPY PHOTOS")
        copy_images(pos_img0)
        clear_img(image_folder)
        time.sleep(4)
        greetings = generate_greetings(prop_data)
        write_copying(greetings, pos_tel_1 ,1)
        write_copying("¿Te interesa otra propiedad? Pasanos el código", pos_tel_1, 1)
        send_contact(prop_data['key'], telephone, message)
        #--DB
        cursor.execute(sql_insert, (telephone, message, status))
        #--
    else:
        status = 2 # No se entiende el mensaje|
    #     if not ('PODEMOS' in message and 'RESPONDERTE' in message):
        greetings = generate_greetings_failed()
        write_copying(greetings, pos_tel_1, 1)
        #--DB
        cursor.execute(sql_insert, (telephone, message, status))
        #--DB
    db.commit()
        #--
###########################################################


if __name__ == "__main__":
    force = 1
    synchronice = 1

    # sync_images()
    # sync(loc)

    # --DB
    db = sqlite3.connect('db_conversations')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY,
        phone TEXT,
        message TEXT,
        status INTEGER)
    ''')
    db.commit()
    # --

    last_telephone = ''
    repeated_telephone = 0
    i_tel = 0

    while 1:
        # Sincronizacion
        if synchronice % 30 == 0:
            sync_images()
            sync(loc)
        synchronice += 1
        # --
        pyperclip.copy('')
        print("Leyendo tel")
        telephone = read_phone_number(tupla_pos_tel[i_tel], region_tel_1)
        print(f"telefono: {telephone}")
        # Logica de Scroll
        print("SCROLLEANDO ABAJO")
        pyautogui.scroll(scroll_amount)

        if telephone == last_telephone:
            print("El telefono se repite")
            repeated_telephone += 1

            if repeated_telephone == 2:
                print("Moviendo el mouse a la siguiente posicion")
                if i_tel < len(tupla_pos_tel) - 1:
                    i_tel += 1

            if repeated_telephone == 3:
                print("SCROOLLEANDO ARRIBA")
                pyautogui.scroll(scroll_up)
                i_tel = 0

        else:
            last_telephone = telephone
            repeated_telephone = 0
        # --
        # Responder Mensajes
        print("Cerrar Spam")
        close_spam(tupla_pos_tel[i_tel], pos_bnt_no_es_spam, region_new_contact)
        print("Leer Mensaje")
        message = read_last_message(pos_new_text, region_new_text)
        print(f"Mensaje: {message}")
        if message == '':
            print("Cerrar Frame de respuesta")
            close_res_frame(pos_res_frame)
            print(f"MENSAJE: {message}")
            message = read_last_message(pos_new_text, region_new_text)

        if not check_if_message_was_answered(message, telephone):
            get_data_and_response(message, telephone)
        # --
        time.sleep(4)
