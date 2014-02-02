"""
 provide web site for colony-live system

"""

import os
import web
import hashlib
import datetime
import subprocess

# set to web folder 
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)

#web.config.debug = False

from clive.core.version import get_version
from clive.core.conf import Configure
from clive.io.tmp import DIR_TMP
from clive.db.handler import ScannerHandler, ExpHandler, PersonHandler
from monitor import ScanStatus, ScanOrder
from scheduler import ScheduleManager
from download import make_growth_csv

cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))
HOUR_GAP = int(cfg[('web','hour_gap')])

VERSION = get_version()

scanner_handler = ScannerHandler()
exp_handler = ExpHandler()
person_handler = PersonHandler()
schedule_manager = ScheduleManager()
scan_status = ScanStatus()
scan_start = ScanOrder('start')
scan_abort = ScanOrder('abort')

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
        print session.loggedin
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
        
        p = subprocess.Popen(["python", "./adduser.py",
            inputs.user,
            inputs.password,
            inputs.name,
            inputs.email],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        outs = [i.replace("\n","<br>") for i in p.stdout]
        output = "".join(map(str,outs))
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

        p = subprocess.Popen(["python", "./register.py",
            str(session.person_id),
            inputs.project,
            dt_start,
            inputs.plate_ids,
            inputs.medium,
            inputs.h_scan,
            conditions_key,
            conditions_value],\
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        #outs = [i.replace("\n","<br>") for i in p.stdout]
        tmp = [i for i in p.stdout]
        output = "".join(map(str,tmp))
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
        schedule_manager.reload()
        
        table = self._make_table()
        calender = self._make_calender()
        return render.reg_manage(self.title, table, calender)

    def POST(self):
        inputs = web.input()
        session.scan_inputs = inputs
        #self.cancel_batch(int(inputs.cancel_ind), session.person_id)
        schedule_manager.cancel(int(inputs.cancel_ind))
        schedule_manager.reload()
        table = schedule_manager.make_table()
        calender = schedule_manager.make_calender()
        return render.reg_manage(self.title, table, calender)
    
    def _make_table(self):
        p = subprocess.Popen(["python", "scheduler.py", 'table'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        #tmp = [i.replace("\n","<br>\n") for i in p.stdout]
        tmp = [i for i in p.stdout]
        html = "".join(map(str,tmp))
        return html
    
    def _make_calender(self):
        p = subprocess.Popen(["python", "scheduler.py", 'calender'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        #tmp = [i.replace("\n","\n") for i in p.stdout]
        tmp = [i for i in p.stdout]
        html = "".join(map(str,tmp))
        return html


#
# Scanning monitor
# 
class monitor:
    title = 'Monitor'

    def GET(self):
        check_login()
        status = scan_status.make_table()
        start = scan_start.make_button(session.person_id)
        abort = scan_abort.make_button(session.person_id)
        return render.monitor(self.title, status, start, abort)

    def POST(self):
        error = ''
        out = ''
        inputs = web.input()
        
        # run
        if inputs.keys()[0].startswith("start"):
            ref_code = inputs.keys()[0]
            ind = int(ref_code.split('-')[1])
            scan_start.submit(ind)
        # stop
        if inputs.keys()[0].startswith("abort"):
            ref_code = inputs.keys()[0]
            ind = int(ref_code.split('-')[1])
            scan_abort.submit(ind)

        status = scan_status.make_table()
        start = scan_start.make_button(session.person_id)
        abort = scan_abort.make_button(session.person_id)
        return render.monitor(self.title, status, start, abort)


class Download:
    title = 'Download'
    
    def GET(self):
        check_login()
        return render.download(self.title, cont='')

    def POST(self):
        inputs = web.input()
        try:
            exp_id = int(inputs['exp_id'])
        except:
            return render.download(self.title)
        
        cont = make_growth_csv(exp_id)
        
        return render.download(self.title, cont)
            

if __name__ == "__main__":
    app.run() 
