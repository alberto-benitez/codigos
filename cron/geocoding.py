#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geopy import geocoders
from geopy.geocoders import Nominatim
from pprint import pprint
import re, time, os
g_api_key = 'AIzaSyDEUj6HlIO44-qtWxsrnDFQqNQw0jLStjk'
g_api_key = ''

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)
g = geocoders.GoogleV3(g_api_key)
#~ g2 = Nominatim()

f = open(os.path.dirname(os.path.abspath(__file__)) + "/../configuration.php")
content = f.read()
f.close()

host = re.findall("\$host = '(.*)'", content)[0]
user = re.findall("\$user = '(.*)'", content)[0]
password = re.findall("\$password = '(.*)'", content)[0]
db = re.findall("\$db = '(.*)'", content)[0]
dbprefix = re.findall("\$dbprefix = '(.*)'", content)[0]



#ejecución remota contra producción
#~ host = "tudomus.com"
#~ user = "root"
#~ password = "T2d0mus@"
#~ db = "dev_tudomus"




import unicodedata, re

all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
# or equivalently and much more efficiently
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))

control_char_re = re.compile('[%s]' % re.escape(control_chars))

def remove_control_chars(s):
    return control_char_re.sub('', s)


import MySQLdb as mdb

deep_mode = False

print host, user, password, db
con = mdb.connect(host, user, password, db);

with con: 

    cur = con.cursor(mdb.cursors.DictCursor)
    if not deep_mode:
        cur.execute("select a.id, c.name country, p.name province, t.name town, a.postal_code, a.address1, a.address2 \
            from %studomus_address a \
            left join %studomus_country c on c.id = a.country_id \
            left join %studomus_province p on p.id = a.province_id \
            left join %studomus_town t on t.id = a.town_id \
            where latitude = 0 and longitude = 0 order by id desc limit 500" % (dbprefix, dbprefix, dbprefix, dbprefix) )
    else:
        
        cur.execute("select a.id, c.name country, p.name province, t.name town, a.postal_code, a.address1, a.address2 \
            ,a.latitude, a.longitude \
            from %studomus_address a \
            left join %studomus_country c on c.id = a.country_id \
            left join %studomus_province p on p.id = a.province_id \
            left join %studomus_town t on t.id = a.town_id \
            inner join (select count(*), latitude, longitude from tdc14_tudomus_address where latitude is not null group by  latitude, longitude having count(*) > 1) t\
            on t.latitude = a.latitude and t.longitude = a.longitude \
            where a.latitude > 0 and a.latitude is not null order by id desc limit 500" % (dbprefix, dbprefix, dbprefix, dbprefix) )

    rows = cur.fetchall()
    
    for row in rows:
        country = ""
        if 'country' in row and row['country']:
            country = row['country'].decode("latin1")
        province = ""
        if 'province' in row and row['province']:
            province = row['province'].decode("latin1")
        if not country and not province:
            continue
        town = ""
        if 'town' in row and row['town']:
            town = row['town'].decode("latin1")
        if not province and not town:
            continue    
        
        address = row['address1'].decode("latin1")
        address2 = row['address2'].decode("latin1")
        

        
        query = remove_control_chars(", ".join([country, province, town, address]))


        if deep_mode:
            
                
            #añade el número de la calle en random
            
            from random import randint
            n_query = query + " %d" %randint(1,100)
            print n_query
            
            geo = g.geocode(n_query)
            #~ geo2 = g2.geocode(n_query)
            if geo and (has_numbers(query) or has_numbers(address2)):
                #ya tiene el número de la calle, es correcto, no se cambia
                continue
        else:
            geo = g.geocode(query)
            
            
        if not geo:
            query = ", ".join([country, province, town, address])
            if deep_mode:
                print "1 ", query
                exit()
            geo = g.geocode(query)
        
        if not geo:
            query = ", ".join([country, province, town])
            if deep_mode:
                print "2 ", query
                exit()
            geo = g.geocode(query)
        
        if not geo:
            print "NO", country, province, town, address
            exit()
            
        
        if deep_mode and float(row['latitude']) == float(geo[1][0]):
            print "En el mismo sitio"
            print repr(geo)
            #~ pprint(geo2)
            print query
            exit()
            
            
        cur.execute("UPDATE %studomus_address set latitude = '%s', \
                longitude = '%s' where id = '%s'" % (dbprefix, 
                geo[1][0], geo[1][1], row['id']))
        
        #~ print "UPDATE %studomus_address set latitude = '%s', \
                #~ longitude = '%s' where id = '%s'" % (dbprefix, 
                #~ geo[1][0], geo[1][1], row['id'])
        
        con.commit()
        
        time.sleep(1)
        
            
        

    
