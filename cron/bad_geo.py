#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import re, time, os, csv

f = open(os.path.dirname(os.path.abspath(__file__)) + "/../configuration.php")
content = f.read()
f.close()

host = re.findall("\$host = '(.*)'", content)[0]
user = re.findall("\$user = '(.*)'", content)[0]
password = re.findall("\$password = '(.*)'", content)[0]
db = re.findall("\$db = '(.*)'", content)[0]
dbprefix = re.findall("\$dbprefix = '(.*)'", content)[0]


smtp_host = re.findall("\$smtphost = '(.*)'", content)[0]
smtp_pass = re.findall("\$smtppass = '(.*)'", content)[0]
smtp_user = re.findall("\$smtpuser = '(.*)'", content)[0]
smtp_port = re.findall("\$smtpport = '(.*)'", content)[0]
tmp_path = re.findall("\$tmp_path = '(.*)'", content)[0]



#ejecución remota contra producción
#~ host = "tudomus.com"
#~ user = "root"
#~ password = "T2d0mus@"
#~ db = "dev_tudomus"


import datetime

if not os.path.exists(tmp_path):
    tmp_path =""

now = datetime.datetime.now()
csv_filename = os.path.join(tmp_path, "bad_geo%04d%02d%02d.csv" % (now.year, now.month, now.day))

import MySQLdb as mdb


con = mdb.connect(host, user, password, db);

with con: 

    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("select pr.id, a.name \
        from %studomus_address a \
        inner join %studomus_property pr on pr.address_id = a.id \
        left join %studomus_country c on c.id = a.country_id \
        left join %studomus_province p on p.id = a.province_id \
        left join %studomus_town t on t.id = a.town_id \
        inner join (select count(*), latitude, longitude from tdc14_tudomus_address where latitude is not null group by  latitude, longitude having count(*) > 1) t\
        on t.latitude = a.latitude and t.longitude = a.longitude \
        where a.latitude > 0 and a.latitude is not null order by id desc" % (dbprefix, dbprefix, dbprefix, dbprefix, dbprefix) )

    rows = cur.fetchall()
    send = False
    with open(csv_filename, 'wb') as csvfile:
        send = True
        writer = csv.writer(csvfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow([row['id'], row['name'], 
            "http://tudomus.dev/index.php?option=com_tudomus&view=property&id=%s" % row['id'], 
            "http://tudomus.dev/administrator/index.php?option=com_tudomus&view=property&layout=edit&id=%s" % row['id']])


if not send:
    exit()

import smtplib
import base64




# Read a file and encode it into base64 format
fo = open(csv_filename, "rb")
filecontent = fo.read()
encodedcontent = base64.b64encode(filecontent)  # base64

marker = "AUNIQUEMARKER"

body ="""
Viviendas posicionadas en el mismo punto.
"""
# Define the main headers.
part1 = """From: <%s>
To: <%s>
Subject: Viviendas mal posicionadas
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=%s
--%s
""" % (smtp_user, smtp_user, marker, marker)

# Define the message action
part2 = """Content-Type: text/plain
Content-Transfer-Encoding:8bit

%s
--%s
""" % (body,marker)
filename = csv_filename.split("/")[-1]
# Define the attachment section
part3 = """Content-Type: multipart/mixed; name=\"%s\"
Content-Transfer-Encoding:base64
Content-Disposition: attachment; filename=%s

%s
--%s--
""" %(filename, filename, encodedcontent, marker)
message = part1 + part2 + part3

try:
   print smtp_host, smtp_port
   smtpObj = smtplib.SMTP( smtp_host , smtp_port)
   smtpObj.login(smtp_user, smtp_pass)
   sender =  smtp_user
   reciever = (smtp_user, "fercalo@hotmail.com")
   smtpObj.sendmail(sender, reciever, message)
   print "Successfully sent email"
except Exception:
   raise
