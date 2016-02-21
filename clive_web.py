#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Webサービス用プログラム

http://ipaddress:8080/でアクセスする

各classはweb pageと対応している
詳しくはwebpyのdocumentを参照
"""

__version__ = "0.0.1"
__date__ = "10 January 2016"


import os
import web
import datetime

# set to web folder 
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)

#web.config.debug = False
#from clive.core.version import get_version
from clive.core.conf import Configure
from clive.db.schema import Scanner, Person, Batch

DIR_TMP = "/tmp/colonylive/"
if not os.path.exists(DIR_TMP):
    cmd = "mkdir -p %s" % DIR_TMP
    os.system(cmd)


cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))
VERSION = cfg[('core','version')]
DAYS_SCHEDULE = int(cfg[('schedule','days')])


# classとURLの対応付け
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


#   Render setting
#render = web.template.render(path+'/templates/')
render = web.template.render(path + '/clive/web/templates/')
web.template.Template.globals['render'] = render
web.template.Template.globals['session'] = session
session.version = VERSION



from clive.db.search import find_person
class login:
    """
    UsernameとPasswordで認証
    認証後  loggedin = 1 となり/monitorへと移動
    """
    def GET(self):
        if session.loggedin:
            raise web.seeother('/monitor')
        else:
            return render.login() 

    def POST(self):
        user = web.input().user
        pwd  = web.input().passwd
        res = find_person(user, pwd) # 存在しない場合はNone
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



class Userreg:
    """
    Userを登録する
    """
    def GET(self):
        return render.user_reg('user_reg', '')

    def POST(self):
        inputs = web.input()
        output = add_user(inputs.user,
                inputs.password,
                inputs.name,
                inputs.email)
        return render.user_reg('user_reg', output)



from clive.db.search import get_all_booked_batchs
from clive.db.register import make_reservation
from clive.web.decode import decode_text
class Expreg:
    """
    実験を登録する

    sid2aryは scanner ID毎のnumpy arrayである
    スキャナーの使用状況を管理（mapping）するためのもの
    """

    def GET(self):
        check_login()
        year, month, day, hour = self._get_dt()
        return render.exp_reg('exp_reg', '', year, month, day, hour)

    def POST(self):
        # inputの整形
        inputs = web.input()
        tmp = "%s-%s-%s-%s" % (inputs.year,inputs.month,inputs.day,inputs.hour)
        dt_start = datetime.datetime.strptime(tmp, '%Y-%m-%d-%H')
        dt_offset = datetime.timedelta(hours=1)
        error = 0
        if dt_start < datetime.datetime.now()-dt_offset:
            error = "Wrong datetime (must be in future)"
        try:
            pairs = decode_text(inputs.text_setting)
        except:
            error = "Wrong input: Conditions&Plates"

        if error != 0:
            year, month, day, hour = self._get_dt()
            return render.exp_reg('exp_reg', error, year, month, day, hour)
    
        # 登録
        batch = Batch()
        batch.set_maxid()
        batch.project = inputs.project
        batch.person_id = session.person_id
        batch.num_plates = len(pairs)
        batch.medium = inputs.medium
        batch.dt_start = dt_start
        batch.h_scan = inputs.h_scan
        batch.status = "waiting the experiment"
        
        batchs = get_all_booked_batchs()
        sid2ary = make_sid2ary(batchs, SCANNER_IDS, DAYS_SCHEDULE)
        error = make_reservation(batch, sid2ary, pairs)
        year, month, day, hour = self._get_dt()
        if error == 0:
            raise web.seeother('/reg_manage')
        return render.exp_reg('exp_reg', error, year, month, day, hour)
        
    def _get_dt(self): 
        now = datetime.datetime.now()
        return now.year, now.month, now.day, now.hour



from clive.web.htmlmaker import get_html_booktable, make_calender
from clive.db.control import cancel_batch
from clive.db.register import make_sid2ary
class Regmanage:
    """
    実験(batch)を管理する

    batchの削除
    未実験の確認ができる(当日から14日後まで）
    """

    title = 'Registrated info'

    def GET(self):
        check_login()
        batchs = get_all_booked_batchs()
        return render.reg_manage(self.title, 
            self.get_html_booktable(batchs),
            self.get_html_calender(batchs))

    def POST(self):
        inputs = web.input()
        batchs = get_all_booked_batchs()
        batch = [i for i in batchs if i.id == int(inputs.batchid_rm)][0]
        cancel_batch(batch)
        # cancelした情報を反映するために再度登録batchを読みこむ
        batchs = get_all_booked_batchs()
        return render.reg_manage(self.title, 
            self.get_html_booktable(batchs), 
            self.get_html_calender(batchs))

    def get_html_booktable(self, batchs):
        for batch in batchs:
            batch.person_name = Person(batch.person_id).name
        return get_html_booktable(batchs)
        
    def get_html_calender(self, batchs):
        sid2ary = make_sid2ary(batchs, SCANNER_IDS, DAYS_SCHEDULE)
        return make_calender(batchs, sid2ary)
    


from clive.db.search import get_my_booked_batchs
from clive.db.control import start_batch, cancel_batch, abort_batch
from clive.web.htmlmaker import get_html_scanstatus, get_html_button
class monitor:
    """
    Scannerの稼動状況を調べ、実験を開始する
    """

    title = 'Monitor'

    def GET(self):
        check_login()
        return render.monitor(self.title,
                    self.get_scanstatus(), self.get_button())

    def POST(self):
        inputs = web.input()
        print inputs.keys()
        ref_code = inputs.keys()[0]
        btype, ind = ref_code.split("-")
        
        batchs = get_my_booked_batchs(session.person_id)
        if btype == "Start":
            batch = [i for i in batchs if i.id == int(ind)][0]
            start_batch(batch)
        if btype == "Cancel":  # cancelは停止させるが終了しない（条件が残る）
            batch = [i for i in batchs if i.id == int(ind)][0]
            cancel_batch(batch)
        if btype == "Abort":   # abortは停止させて終了する。
            batch = [i for i in batchs if i.id == int(ind)][0]
            abort_batch(batch)
        return render.monitor(self.title,
                    self.get_scanstatus(), self.get_button())
    
    def get_scanstatus(self):
        scanners = [Scanner(i) for i in SCANNER_IDS]
        return get_html_scanstatus(scanners)
    
    def get_button(self):
        batchs = get_my_booked_batchs(session.person_id)
        return get_html_button(session.person_id, batchs)



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

if __name__ == "__main__":
    app.run() 

