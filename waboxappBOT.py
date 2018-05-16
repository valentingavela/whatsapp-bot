import mysql.connector

#para correr este programa hay que abrir un tunnel
#ssh ubuntu@benteveo.com -L 3306:127.0.0.1:3306 -N &
cnx = mysql.connector.connect(user='benteveo_root',
                              password='bichofeo',
                              host='127.0.0.1',
                              database='benteveo_siguitds')

# cursor = cnx.cursor()
cursor = cnx.cursor(dictionary=True)
cursor.execute("select * from wspbot_msg where est=0")

for rec in cursor:
    tel = rec['con_tel']
    msg = rec['msg_body']

    print(tel, msg)

cursor.close()
cnx.close()
