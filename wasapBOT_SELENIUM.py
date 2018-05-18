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
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from PIL import ImageChops
from datetime import datetime
import subprocess
import random

os.chdir('/home/wasap/whatsapp-bot')
driver = None
DBG = 1
loc = 3

##########
# El ZOOM de la pagina esa en 125%
##########
pyautogui.FAILSAFE = True
urlimg = 'http://www.benteveo.com/siguit-inmo/images/'
imageFolder = "/home/wasap/whatsapp-bot/media/"

# COORDENADAS WASAP:
regionTelSup = (1117, 91, 1308, 125)  # El num de telefono que aparece arriba
posMsj1 = (854, 392)  # posicion del mensaje nuevo a la izquierda
posNewText = (1077, 652)  # El ultimo texto que manda el usuario en la zona de conversacion
regionNewText = (1039, 633, 1547, 679)  # Region donde aparece el ultimo texto
regionMessages = (660, 361, 1020, 712)  # zona donde estan todos los mensajes recibidos
regNewContact = (1242, 628, 1385, 660)  # Boton "NO ES SPAM" del cartel de spam
posBntNoEsSpam = (1321, 646)  # Posicion del boton de "NO ES SPAM"
regResFrame = (1527, 636, 1580, 677)  # Region donde aparece la X para cerrar un cuadro de respuesta
posResFrame = (1556, 656)


# COORDENADAS FILE MANAGER
posFolder = (262, 113)  # filemanager
posImg0 = (262, 113)  # Primer imagen en el filemanager
posTextBox = (1400, 400)  # caja donde se encuentra la conversacion

scrolling = (-2.1)




def nuevosmensajes(messagesframezone):
    im1 = pyscreenshot.grab(bbox=messagesframezone)
    time.sleep(3)
    im2 = pyscreenshot.grab(bbox=messagesframezone)
    diff = ImageChops.difference(im1, im2)

    if diff.getbbox():
        return True
    else:
        return False


###########################################################


def leernum(posmsj, reg):
    pyautogui.click(posmsj)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    return text.upper()


def leermsj(pos, reg):
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


def guardar(tel):
    # TODO guardar el numero de telefono en la base de datos
    pass


###########################################################


def guardarfoto(url, path):
    print("guardando fotos")
    response = requests.get(url)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)

    img_data = requests.get(url).content
    with open(path + extension, 'wb') as handler:
        handler.write(img_data)


###########################################################


def ctrla():
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)


def copiarimg(regImg):
    print("copiando img")
    pyautogui.moveTo(regImg)
    pyautogui.click(regImg)
    time.sleep(1)
    ctrla()
    # Arrastro las imagenes
    pyautogui.moveTo(regImg, duration=1)
    pyautogui.dragTo(posTextBox[0], posTextBox[1], 2, button='left')
    time.sleep(8)
    pyautogui.press('enter')


###########################################################


def clearimg(dirpath):
    file_list = os.listdir(dirpath)
    for fileName in file_list:
        os.remove(dirpath + "/" + fileName)


###########################################################


def write_with_keyboard(msj):
    print("Escribiendo rta")
    print(msj)
    # pyautogui.click(posTextFrame)
    pyautogui.click(posMsj1)
    time.sleep(0.4)
    for letra in msj:
        if letra == 'ñ':
            copypaste('ñ')
        elif letra == 'á':
            copypaste('á')
        elif letra == 'é':
            copypaste('é')
        elif letra == 'í':
            copypaste('í')
        elif letra == 'ó':
            copypaste('ó')
        elif letra == 'ú':
            copypaste('ú')
        elif letra == 'ü':
            copypaste('ü')
        elif letra == ':':
            copypaste(':')
        elif letra == '/':
            copypaste('/')
        elif letra == '¿':
            copypaste('¿')
        elif letra == '?':
            copypaste('?')
        else:
            pyautogui.typewrite(letra)
        #time.sleep(0.05)
    pyautogui.press('enter')


def copypaste(m):
    if DBG: print('F: Copypaste')
    pyperclip.copy(m)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')





def generarrespuesta1(data_prop, codigo):
    rta = data_prop
    return rta


def generarfooter(data, texto):
    print("Generando Footer")
    prod_nom = ""
    prod_tel = ""

    footer = ""
    for i in data['schedule']:
        codigo = i["Cod"]
        if codigo in texto:
            prod_nom = i['prod_nom']
            prod_tel = i['prod_tel']

    if prod_nom != "" :
        footer += f"Si te interesa esta propiedad comunicate con {prod_nom} tel: {prod_tel} \n"

    footer += "¿Te interesa otra propiedad? Pasanos el código"

    return footer


def sync(loc):
    if DBG: print('F: Sync')
    command = 'rsync -Pavi -e "ssh -i %s/siguit.pem" --itemize-changes ' \
              'siguit@benteveo.com:/var/www/html/siguitds/inmobiliarias/schedule/cli-3.json ' % (os.getcwd())

    command += ' '+os.getcwd() + '/schedule.json'

    output, error = subprocess.Popen(
        command, universal_newlines=True, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if DBG: print(error)
    if DBG: print(output)
    if ".f" in output:
        return 0
    else:
        return 1


###########################################################


def get_propertys_data():
    with open('%s/schedule.json' % (os.getcwd())) as json_data:
        data = json.load(json_data)
        return data


###########################################################
# def check_if_valid_message_code(data, message):
#     print("Obteniendo CODIGO valido")
#     message = message.upper()
#     for i in data['schedule']:
#         codigo = i['Cod']
#         if codigo in message:
#             return codigo


def get_property_data(data, texto):
    print("Buscando Prop en el texto que ingreso el cliente")

    operation_type = ''
    description = ''
    direction = ''
    price = ''
    code = ''
    prod_nom = ''
    prod_tel = ''

    texto = texto.upper()
    b = ''
    # Debo encontrar un codigo valido
    for i in data['schedule']:
        codigo = i['Cod']

        if codigo in texto:
            # if propid == i["reference_code"]:
            if DBG: print('Propiedad encontrada :' + codigo)
            operation_type = i["TipodeOperacion"]
            description = i["Descripcion"]
            direction = i["Direccion"]
            price = i["Precio"]
            prod_nom = i['prod_nom']
            prod_tel = i['prod_tel']
            break

    return {"code" : code, "operation type" : operation_type,
            "description" : description, "direction" : direction,
            "price" : price, "prod_nom" : prod_nom, "prod_tel" : prod_tel}


###########################################################


def generate_response(prop_data):
    response = f"Hola! Gracias por contactarte. En breve te enviamos los datos de la propiedad con el código {prop_data['code']} \n"
    response += f"Tipo de operación: {prop_data['operation_type']} \n"
    response += f"prop_data['description'] \n"
    response += f"Dirección: {prop_data['direction']} \n"
    response += f"Precio: {prop_data['price']} \n"
    response += f"Si te interesa esta propiedad comunicate con {prod_nom} tel: {prod_tel} \n"
    response += "¿Te interesa otra propiedad? Pasanos el código \n"
    return response
###########################################################




def propimg(data, texto, fotodir):
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
                guardarfoto(urlimg + fotourl, fotodir + str(p))
            break
    return p


###########################################################


def archivarchat():
    pyautogui.click(posMsj1, button='right')
    time.sleep(0.3)
    pyautogui.moveRel(100, 40)
    pyautogui.click()


###########################################################


def checkspam(pos, posbtnspam, reg):
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    if text.upper() == 'NO ES SPAM':
        pyautogui.click(posbtnspam)  # Voy a la posicion 1 y clickeo


###########################################################


def chkresframe(pos):
    if DBG: print('Fn: chkresframe')
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo


###########################################################


def run(force):
    # TODO corregir el tema de que cuando es cada 5 minutos busca a cada rato
    if nuevosmensajes(regionMessages) or force:
        print("Nuevo Mensaje")
        checkspam(posMsj1, posBntNoEsSpam, regNewContact)
        tel = leernum(posMsj1, regionTelSup)  # Leo el numero de telefono
        chkresframe(posResFrame)
        if tel:
            print("TEL: " + tel)
            texto = leermsj(posNewText, regionNewText)  # Obtengo el propid del mensaje del remitente
            if DBG == 1: print("TEXTO: " + texto)
            if len(texto) > 3:
                sync(loc)
                data = get_propertys_data()
                if data:
                    codigo = check_if_valid_message_code(data, texto)
                    data_prop = get_property_data(data, texto)
                    if data_prop:
                        print(data_prop)
                        respuesta = generate_response(codigo)
                        write_with_keyboard(respuesta)
                        respuesta = generarrespuesta1(data_prop, codigo)
                        write_with_keyboard(respuesta)
                        if propimg(data, texto, imageFolder):
                            print("Copiando Fotos")
                            copiarimg(posImg0)
                            clearimg(imageFolder)
                        time.sleep(4)
                        textoprod = generarfooter(data, texto)
                        if textoprod:
                            write_with_keyboard(textoprod)
                        if tel == leernum(posMsj1, regionTelSup):
                            archivarchat()


###########################################################
###########################################################


def start_selenium():
    global driver
    driver = webdriver.Chrome("/home/wasap/whatsapp-bot/chromedriver")
    driver.get("https://web.whatsapp.com/")
    answer = input('Is the phone connected successfully? (y/Y) -> ')

    if str(answer).strip().lower() == 'y':
        print("starting")
    else:
        print('Bye')
        exit(0)


###########################################################


def collect_whatsapp_data():
    # Todo: debuugear por que  message ingresa en blanco
    elements = driver.find_elements_by_tag_name("div")
    text = elements[0].text
    text = text.splitlines()

    telephone = ''
    msg_hour = ''
    message = ''
    message_bar = ''
    telephones = []
    base_data = []
    # dic = {}

    # Busqueda de elementos
    for i in range(len(text)):
        line = text[i]
        if line[:1] == '+':
            telephone = line
            telephones.append(telephone)
        elif line[2:3] == ':':
            msg_hour = line
        elif line == 'Sea notificado de mensajes nuevos'\
            or line == 'Activar notificaciones de escritorio' \
            or line.partition(' ')[0] == "Videollamada" \
            or line == 'Buscar o empezar un chat nuevo' \
            or line == 'Escribe un mensaje aquí' \
            or line == 'Mantén tu teléfono conectado' \
            or line == 'WhatsApp se conecta a tu teléfono para sincronizar los mensajes.' \
                       ' Para reducir el consumo de tus datos,' \
                       ' conecta tu teléfono a una red Wi-Fi.' \
                or line == '':
            line = ''
        else:
            message = line
            # print(f"telephone: {telephone} hour: {msg_hour} message: {line}")

        if (telephone and msg_hour and line) != '':
            base_data.append({"telephone": telephone, "hour": msg_hour, "message": message})
    return base_data


###########################################################


def write_contact_in_searchbar(contact_name):
    searchbar = driver.find_elements_by_tag_name("input")
    if(searchbar):
        searchbar[0].click()
        time.sleep(0.2)
        searchbar[0].send_keys(contact_name)
        time.sleep(0.2)
        searchbar[0].send_keys(Keys.ENTER)


###########################################################


def write_message(message):
    message_bar = driver.find_element_by_xpath("//div[@spellcheck]")
    message_bar.click()
    time.sleep(0.1)
    message_bar.send_keys(message)


###########################################################

def parse_and_response(whatsapp_data, data):
    sync(loc)

    code = ''

    for contact in whatsapp_data:

        contact_name = contact['telephone']
        message = contact['message']

        print(f"CONTACTO: {contact_name}")

        #Checkeo si es valido el codigo que me mandaron.
        # code = check_if_valid_message_code(data, message)
        prop_data = get_property_data(data, texto)

        if prop_data['code']:
            # CHECKEAR SI YA FUE CONTESTADO UN MSG ASI
            if not check_in_db_if_responded(contact_name, message):
                #  Comenzamos a responder:
                write_contact_in_searchbar(contact_name)
                response = generate_response(prop_data)
                write_response(response)
###########################################################


def check_in_db_if_responded(contact_name):
    # QUERY
    # select id, con_name, msg_body from wspbot_msg where con_name=contact_name
    return 0


###########################################################

if __name__ == "__main__":
    start_selenium()

    while 1:
        whatsapp_data = collect_whatsapp_data()
        time.sleep(1)

        if whatsapp_data != collect_whatsapp_data():
            print("NEW DATA!")
            parse_and_response(whatsapp_data)
