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

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By

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
url_img = 'http://www.benteveo.com/siguit-inmo/images/'
image_folder = "/home/wasap/whatsapp-bot/media/"

# COORDENADAS WASAP:
pos_msj1 = (854, 392)  # posicion del mensaje nuevo a la izquierda
pos_new_text = (1077, 652)  # El ultimo texto que manda el usuario en la zona de conversacion
pos_bnt_no_es_spam = (1321, 646)  # Posicion del boton de "NO ES SPAM"
pos_res_frame = (1556, 656)
region_tel_sup = (1117, 91, 1308, 125)  # El num de telefono que aparece arriba
region_new_text = (1039, 633, 1547, 679)  # Region donde aparece el ultimo texto
region_messages = (660, 361, 1020, 712)  # zona donde estan todos los mensajes recibidos
region_new_contact = (1242, 628, 1385, 660)  # Boton "NO ES SPAM" del cartel de spam
region_res_frame = (1527, 636, 1580, 677)  # Region donde aparece la X para cerrar un cuadro de respuesta


# COORDENADAS FILE MANAGER
pos_folder = (262, 113)  # filemanager
pos_img0 = (262, 113)  # Primer imagen en el filemanager
pos_text_box = (1400, 400)  # caja donde se encuentra la conversacion
# SCROLL ENTRE MENSAJES
scrolling = (-2.1)


###########################################################


def collect_data():
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
            or line == 'Escribe un mensaje aquí'\
                or line == '':
            line = ''
        else:
            message = line
            # print(f"telephone: {telephone} hour: {msg_hour} message: {line}")

        if (telephone and msg_hour and line) != '':
            base_data.append({"telephone": telephone, "hour": msg_hour, "message": message})

    return base_data


###########################################################


def find_contact(user_name):
    searchbar = driver.find_elements_by_tag_name("input")
    if(searchbar):
        searchbar[0].click()
        time.sleep(0.2)
        searchbar[0].send_keys(user_name)
        time.sleep(0.2)
        searchbar[0].send_keys(Keys.ENTER)


###########################################################


def write_message(message):
    message_bar = driver.find_element_by_xpath("//div[@spellcheck]")
    message_bar.click()
    time.sleep(0.1)
    message_bar.send_keys(message)


###########################################################
def check_for_new_messages_graphical(messagesframezone):
    im1 = pyscreenshot.grab(bbox=messagesframezone)
    time.sleep(3)
    im2 = pyscreenshot.grab(bbox=messagesframezone)
    diff = ImageChops.difference(im1, im2)

    if diff.getbbox():
        return True
    else:
        return False
###########################################################


def read_phone_number(posmsj, reg):
    pyautogui.click(posmsj)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    return text.upper()


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


def save_telephone(tel):
    # TODO guardar el numero de telefono en la base de datos
    pass


###########################################################


def download_images(url, path):
    print("guardando fotos")
    response = requests.get(url)
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)

    img_data = requests.get(url).content
    with open(path + extension, 'wb') as handler:
        handler.write(img_data)


###########################################################


def ctrl_a():
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)


def copy_images(region_image):
    print("copiando img")
    pyautogui.moveTo(region_image)
    pyautogui.click(region_image)
    time.sleep(1)
    ctrl_a()
    # Arrastro las imagenes
    pyautogui.moveTo(region_image, duration=1)
    pyautogui.dragTo(pos_text_box[0], pos_text_box[1], 2, button='left')
    time.sleep(3)
    pyautogui.press('enter')
    time.sleep(1)


###########################################################


def clear_img(dirpath):
    file_list = os.listdir(dirpath)
    for fileName in file_list:
        os.remove(dirpath + "/" + fileName)
###########################################################


def write(msj):
    print("Escribiendo rta")
    print(msj)
    # pyautogui.click(posTextFrame)
    pyautogui.click(pos_msj1)
    time.sleep(0.4)
    for letra in msj:
        if letra == 'ñ':
            copy_paste('ñ')
        elif letra == 'á':
            copy_paste('á')
        elif letra == 'é':
            copy_paste('é')
        elif letra == 'í':
            copy_paste('í')
        elif letra == 'ó':
            copy_paste('ó')
        elif letra == 'ú':
            copy_paste('ú')
        elif letra == 'ü':
            copy_paste('ü')
        elif letra == ':':
            copy_paste(':')
        elif letra == '/':
            copy_paste('/')
        elif letra == '¿':
            copy_paste('¿')
        elif letra == '?':
            copy_paste('?')
        else:
            pyautogui.typewrite(letra)
        #time.sleep(0.05)
    pyautogui.press('enter')
###########################################################


def write_copying(msj):
    print(msj)
    pyautogui.click(pos_msj1)
    time.sleep(0.4)
    copy_paste(msj)
    time.sleep(0.1)
    pyautogui.press('enter')
###########################################################


def copy_paste(m):
    if DBG: print('F: Copypaste')
    pyperclip.copy(m)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
###########################################################


def generarrespuesta(codigo):
    rta = "Hola! Gracias por contactarte. En breve te enviamos los datos de la propiedad con el código " + codigo + "."
    return rta
###########################################################


def generarrespuesta1(data_prop, codigo):
    rta = data_prop
    return rta
###########################################################


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
###########################################################


def sync(loc):
    #TODO: que sincronize TODAS las propiedades
    if DBG: print('F: Sync')
    command = 'rsync -Pavi -e "ssh -i %s/siguit.pem" --itemize-changes ' \
              'siguit@benteveo.com:/var/www/html/siguitds/inmobiliarias/schedule/all_props.json ' % (os.getcwd())

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


def sync_images():
    if DBG: print('F: Sync Images')
    command = f'rsync -e "ssh -i {os.getcwd()}/siguit.pem" -r' \
              f' siguit@benteveo.com:/var/www/html/siguitds/inmobiliarias/images/ {os.getcwd()}/all_media'

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
def obtenerId(data, texto):
    print("Obteniendo ID")
    texto = texto.upper()
    for i in data['schedule']:
        codigo = i['Cod']
        if codigo in texto:
            return codigo


def buscarporpropid(data, texto):
    print("buscando prop segun el texto que ingreso el cliente")
    texto = texto.upper()
    b = None
    # Debo encontrar un codigo valido
    for i in data['schedule']:
        codigo = i['Cod']
        if DBG: print('Codigo Disponible :' + codigo)
        # difflib.get_close_matches(codigo, texto.split())
        if codigo in texto:
            # if propid == i["reference_code"]:
            print("Prop Encontrada")
            b = str(i["TipodeOperacion"]) + "\n"
            b += str(i["Descripcion"]) + "\n"
            b += "Dirección " + i["Direccion"] + "\n"
            b += "Precio " + str(i["Precio"]) + "\n"

            break
        else:
            # rtas = ['prop no encontrada', 'lo siento', 'no la encuentro']
            # b = random.choice(rtas)
            b = ''
    return b


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


def archive_chat():
    pyautogui.click(pos_msj1, button='right')
    time.sleep(0.3)
    pyautogui.moveRel(100, 40)
    pyautogui.click()


###########################################################


def check_spam(pos, posbtnspam, reg):
    pyautogui.click(pos)  # Voy a la posicion 1 y clickeo
    im = pyscreenshot.grab(bbox=reg)
    text = pytesseract.image_to_string(im, lang='spa')
    if text.upper() == 'NO ES SPAM':
        pyautogui.click(posbtnspam)  # Voy a la posicion 1 y clickeo


###########################################################


def check_res_frame(pos):
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
                    codigo = obtenerId(data, texto)
                    data_prop = buscarporpropid(data, texto)
                    if data_prop:
                        print(data_prop)
                        respuesta = generarrespuesta(codigo)
                        write(respuesta)
                        respuesta = generarrespuesta1(data_prop, codigo)
                        write(respuesta)
                        if propimg(data, texto, image_folder):
                            print("Copiando Fotos")
                            copy_images(posImg0)
                            clear_img(url_img)
                        time.sleep(4)
                        textoprod = generarfooter(data, texto)
                        if textoprod:
                            write(textoprod)
                        if tel == leernum(posMsj1, regionTelSup):
                            archivarchat()
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
                image_name = image['url']
                # download_images(url_img + image_name, image_folder + str(p))
                print("Copiando imagenes")
                subprocess.call(["cp", f"{os.getcwd()}/all_media/{image_name}", f"{os.getcwd()}/media/{image_name}"])
                p += 1
            break

    return {"key" : key, "code" : code, "operation_type" : operation_type,
            "description" : description, "direction" : direction,
            "price" : price, "prod_nom" : prod_nom, "prod_tel" : prod_tel}


###########################################################


def generate_response(prop_data):
    response = f"Hola! Gracias por contactarte. En breve te enviamos los datos de la propiedad con el código {prop_data['code']} \n\n"
    response += f"Tipo de operación: {prop_data['operation_type']} \n\n"
    if prop_data['description']:
        response += f"{prop_data['description']} \n\n"
    response += f"Dirección: {prop_data['direction']} \n\n"
    response += f"Precio: {prop_data['price']} \n\n"
    return response
###########################################################


def generate_greetings(prop_data):
    response = ''
    if(prop_data['prod_nom']):
        response += f"Si te interesa esta propiedad comunicate con {prop_data['prod_nom']} tel: {prop_data['prod_tel']} \n\n"
    # response += "¿Te interesa otra propiedad? Pasanos el código \n\n"
    return response



def generate_greetings_failed(telephone='1158717399'):
    response = f"Podemos responderte via Whatsapp sobre nuestras propiedades ofertadas. \
    Para cualquier otra consulta te recomiendo comunicarte con la Inmobiliaria al teléfono \
    {telephone} Si querés consultar sobre alguna propiedad en particular, pasanos su código."
    return response



###########################################################


def send_contact(key, cellphone, message):
    # url = "https://www.tokkobroker.com/api/v1/webcontact/?key=c6b7f558fb879c9dcbec357d28fc0c564a443108"
    url = f"https://www.tokkobroker.com/api/v1/webcontact/?key={key}"
    msg = f"Han enviado el siguiente mensaje: {message}"
    payload={"name": cellphone, "tag": "bot", "cellphone" : cellphone, "text" : msg}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(r.status_code, r.reason)
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
        write_copying(response)
        print("COPY PHOTOS")
        copy_images(pos_img0)
        clear_img(image_folder)
        time.sleep(4)
        greetings = generate_greetings(prop_data)
        write_copying(greetings)
        write_copying("¿Te interesa otra propiedad? Pasanos el código")
        send_contact(prop_data['key'], telephone, message)
        #--DB
        cursor.execute(sql_insert, (telephone, message, status))
        #--
    else:
        status = 2 # No se entiende el mensaje
    #     if not ('PODEMOS' in message and 'RESPONDERTE' in message):
        greetings = generate_greetings_failed()
        write_copying(greetings)
        #--DB
        cursor.execute(sql_insert, (telephone, message, status))
        #--DB
    db.commit()
        #--
###########################################################


def new_work(force):
    pyperclip.copy('')
    if check_for_new_messages_graphical(region_messages) or force:
        print("New messages or forcing new messags")
        check_spam(pos_msj1, pos_bnt_no_es_spam, region_new_contact)
        check_res_frame(pos_res_frame)
        telephone = read_phone_number(pos_msj1, region_tel_sup)

        if telephone:
            message = read_last_message(pos_new_text, region_new_text)
            print("MENSAJE" + message)
            ###TODO: messages
            #Deberia checkear todos los mensajes quizas con un crtl+A:
            # messages = read_all_messages()
            #Checkear en la base de datos:
            if not check_if_message_was_answered(message, telephone):
                get_data_and_response(message, telephone)
            # if telephone == read_phone_number(pos_msj1, region_tel_sup):
            #     archive_chat()
###########################################################

# todo: checkear si ya conteste los mensajes a tal numero.
# todo si a tal numero no conteste tal mensaje , mandar mensaje de  "no etiendo"


if __name__ == "__main__":
    force = 1
    synchronice = 1

    sync_images()
    sync(loc)

    #--DB
    db = sqlite3.connect('db_conversations')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY,
        phone TEXT,
        message TEXT,
        status INTEGER)
    ''')
    db.commit()

    #--

    while 1:
        if synchronice % 10 == 0:
            sync_images()
            sync(loc)
        synchronice += 1

        new_work(force)


#DB EXAMPLE
# import sqlite3
# db = sqlite3.connect('db_conversations')
# cursor = db.cursor()
# cursor.execute('''
#     CREATE TABLE conversations(id INTEGER PRIMARY KEY,
#     phone TEXT,
#     message TEXT,
#     status INTEGER)
# ''')
# db.commit()
# #--
#
# phone = "32132132133"
# message = "pepepe"
# status = 1
# cursor.execute('''INSERT INTO conversations(phone, message, status)
#                   VALUES(?,?,?)''', (phone, message, status))
#
# cursor.execute('''SELECT * FROM conversations''')
#
# db.commit()
