#!/usr/bin/python

import sys
import hashlib

from clive.db.handler import PersonHandler

person_handler = PersonHandler()

def add_user(user, passwd, name, email):
    for val in [user,passwd,name,email]:
        if len(val) == 0:
            return "Fill out all fields"
    pass_sha1 = hashlib.sha1(passwd).hexdigest()
    try:
        person_handler.create(user, pass_sha1, name, email)
    except:
        return "Failed"
    return "Success"


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 5:
        print "Usage: %s [user] [pass] [name] [email]" % argvs[0]
        quit()
    user, passwd, name, email = argvs[1:]
    print add_user(user, passwd, name, email)

