#!/usr/bin/python

import sys
import hashlib

from clive.db.handler import PersonHandler

person_handler = PersonHandler()

argvs = sys.argv
if len(argvs) != 5:
    print "Usage: %s [user] [pass] [name] [email]" % argvs[0]
    quit()


for val in argvs[1:]:
    if len(val) == 0:
        print "Fill out all fields"
        quit()

user, passwd, name, email = argvs[1:]


pass_sha1 = hashlib.sha1(passwd).hexdigest()
try:
    person_handler.create(user, pass_sha1, name, email)
    print "Success"
except:
    print "Failed"
