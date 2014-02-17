#!/usr/bin/env python

"""
 provide web site for colony-live system

"""

import os
import web
import hashlib
import datetime
import commands
import subprocess

# set to web folder 
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)

#web.config.debug = False
from clive.core.version import get_version
from clive.core.conf import Configure
from clive.io.tmp import DIR_TMP
from clive.db.handler import ScannerHandler, ExpHandler, PersonHandler
from monitor import get_status
from adduser import add_user
from register import make_reservation
from download import make_growth_csv, make_images_tar
from scheduler import make_schedule_table, make_calender, cancel_schedule
from scan_control import get_list, scan_start, scan_abort

cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))

VERSION = get_version()

scanner_handler = ScannerHandler()
exp_handler = ExpHandler()
person_handler = PersonHandler()

urls = (
    '/', 'login',
    '/login', 'login',
    '/logout', 'logout',
    '/monitor', 'monitor',
    '/user_reg', 'Userreg',
    '/exp_reg', 'Expreg',
    '/reg_manage', 'Regmanage',
    '/download','Download'
)


app = web.application(urls, globals())

# do not modify this
# to deal with debug mode & session problem
if web.config.get('_session') is None:
    session = web.session.Session(\
        app,\
        web.session.DiskStore(DIR_TMP+'/session'),\
        initializer={\
            'loggedin':False ,
            'inputs':'',
            'scan_info':'',
            'exp_info':'',
            'id_inputs':{'selected_item':'plate'},
            'scan_inputs':'',
            'version':VERSION
        }
    )
    web.config._session = session
else:
    session = web.config._session



def session_hook():
    web.ctx.session = session
    web.template.Template.globals['session'] = session

app.add_processor(web.loadhook(session_hook))


# 
#   Render setting
#
#render = web.template.render(path+'/templates/')
render = web.template.render('templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['session'] = session
session.version = VERSION


#
#   Login / Logout 
#
class login:
    def GET(self):
        if session.loggedin:
            raise web.seeother('/monitor')
        else:
            return render.login() 

    def POST(self):
        user, pwd = web.input().user, web.input().passwd
        pass_sha1 = hashlib.sha1(pwd).hexdigest()
        res = person_handler.authenticate(user, pass_sha1)
        if res:
            session.loggedin = True
            session.person_id = res.id
            session.person_name = res.name 
            session.version = VERSION
            raise web.seeother('/monitor')
        else:
            return render.login('Username or Password is wrong.')


class logout:
    def GET(self):
        session.loggedin = 0
        session.kill()
        raise web.seeother('/')


def check_login():
    if not session.loggedin:
        raise web.seeother('/')
    return



#
#   User registration
#
class Userreg:
    def GET(self):
        return render.user_reg('user_reg', '')

    def POST(self):
        inputs = web.input()
        output = add_user(inputs.user,
                inputs.password,
                inputs.name,
                inputs.email)
        return render.user_reg('user_reg', output)


#
#   Experiment registration
#
class Expreg:
    def GET(self):
        check_login()
        year, month, day, hour = self._get_dt()
        return render.exp_reg('exp_reg', '', year, month, day, hour)

    def POST(self):
        inputs = web.input()
        conditions_key = "|".join(
            [inputs.key1, inputs.key2, inputs.key3])
        conditions_value = "|".join(
            [inputs.values1, inputs.values2, inputs.values3])
        dt_start = "%s-%s-%s-%s" % (
            inputs.year,
            inputs.month,
            inputs.day,
            inputs.hour
            )
        values = [
            str(session.person_id),
            inputs.project,
            dt_start,
            inputs.plate_ids,
            inputs.medium,
            inputs.h_scan,
            conditions_key,
            conditions_value]

        output = make_reservation(values)
        year, month, day, hour = self._get_dt()
        return render.exp_reg('exp_reg', output, year, month, day, hour)
        
    def _get_dt(self): 
        now = datetime.datetime.now()
        return now.year, now.month, now.day, now.hour

#
#   Registration management
#
class Regmanage:
    title = 'Registrated info'

    def GET(self):
        check_login()
        inputs = session.scan_inputs
        
        table = make_schedule_table()
        calender = make_calender()
        return render.reg_manage(self.title, table, calender)

    def POST(self):
        inputs = web.input()
        session.scan_inputs = inputs
        
        cancel_schedule(int(inputs.cancel_ind))
        table = make_schedule_table()
        calender = make_calender()
        return render.reg_manage(self.title, table, calender)
    

#
# Scanning monitor
# 
class monitor:
    title = 'Monitor'

    def GET(self):
        check_login()
        status = get_status()
        cont = get_list(session.person_id)
        return render.monitor(self.title, status, cont)

    def POST(self):
        inputs = web.input()
        ref_code = inputs.keys()[0]
        btype, ind = ref_code.split("-")
        ind = int(ind)
        
        # run
        if btype == "start":
            scan_start(session.person_id, ind) 
        # stop
        if btype == "abort":
            scan_abort(session.person_id, ind) 

        status = get_status()
        cont = get_list(session.person_id)
        return render.monitor(self.title, status, cont)


class Download:
    title = 'Download'
    
    def GET(self):
        check_login()
        return render.download(self.title)

    def POST(self):
        inputs = web.input()
        try:
            exp_id = int(inputs['exp_id'])
        except:
            return render.download(self.title)

        if inputs['item'] == "image":
            data = make_images_tar(exp_id)
            fname = "%d.zip" % exp_id
            web.header("Content-Disposition", "attachment; filename=%s" % fname)
            web.header("Content-Length", len(data))
            web.header("Content-Type", "application/octet-stream")
            return data
    
        if inputs['item'] == "growth":
            data = make_growth_csv(exp_id)
            fname = "%d.csv" % exp_id
            web.header("Content-Disposition", "attachment; filename=%s" % fname)
            web.header("Content-Length", len(data))
            web.header("Content-Type", "text/csv")
            return data
            

if __name__ == "__main__":
    app.run() 
