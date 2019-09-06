#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint

url_login = "http://tudomus.dev/administrator/index.php"
url = "http://tudomus.com/administrator/index.php?option=com_joomailermailchimpintegration&task=copyCampaign"



post = {
    "username" : "hola@fernandocalo.com",
    "passwd" : "Tud0mus14",
    "lang" : ""
}

from lxml.html import parse
dom = parse(url_login).getroot()
inputs = dom.cssselect('input[type="hidden"]')
for _input in inputs:
    post[_input.name] = _input.value
    
pprint(post)

import urllib2, urllib




data = urllib.urlencode(post)
req = urllib2.Request(url_login, data)

response = urllib2.urlopen(req)
print response.info()
html = response.read()
file_html = open("a.html", "w")
file_html.write(html)
file_html.close()
