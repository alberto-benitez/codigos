#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import os, sys, time


def compress_path(path, f):
    print "recorriendo %s" % path
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            compress_path(os.path.join(dirname, subdirname), f)

        # print path to all filenames.
        for filename in filenames:
            if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                compress (os.path.join(dirname, filename), f)

def compress(filename, f):
    print "comprimiendo %s" % filename
    
    pre_size = os.path.getsize(filename)
    
    command = 'jpegtran -copy none -optimize -outfile "%s" "%s"' %\
        (filename, filename)
    os.system(command)
    
    size = os.path.getsize(filename)
    
    f.write("%s %s -> %s\n" % (filename, pre_size, size))
    time.sleep(1)

paths = ["/home/tudomusweb/www/tudomus.com/images/tudomus/properties/"]


_paths = []

for _id in sys.argv[1:]: 
    _paths.append(paths[0] + _id)
    
if _paths:
    paths = _paths

#~ paths.append("/home/tudomusweb/www/tudomus.com/images/tudomus/members/")

f = open("image_compress.log", "w");

for path in paths:
    compress_path(path, f)

f.close()



