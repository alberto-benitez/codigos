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
tmp_path = re.findall("\$tmp_path = '(.*)'", content)[0]

import datetime

if not os.path.exists(tmp_path):
    tmp_path =""

now = datetime.datetime.now()
csv_filename = os.path.join(tmp_path, "visits%04d%02d%02d%02d.csv" % 
    (now.year, now.month, now.day, now.hour))

import MySQLdb as mdb


con = mdb.connect(host, user, password, db);

with con: 

    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("select * from %studomus_property_visit" % dbprefix)
    
    rows = cur.fetchall()
    
    
    with open(csv_filename, 'wb') as csvfile:
        
            
        writer = csv.writer(csvfile, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            
        first = True
        for row in rows:
            if first:
                writer.writerow(row.keys())
                first = False
            writer.writerow(row.values())

print "generado %s " % csv_filename
