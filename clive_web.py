#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Webサービス用プログラム

http://ipaddress:8080/でアクセスする

各classはweb pageと対応している
詳しくはwebpyのdocumentを参照
"""

__version__ = "0.0.1"
__date__ = "03 January 2016"


import os
import web
import datetime

# set to web folder 
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)

#web.config.debug = False
#from clive.core.version import get_version
from clive.core.conf import Configure
from clive.io.tmp import DIR_TMP
from clive.db.schema import Scanner, Person


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
    '/exp_reg_dko', 'Expregdko',
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



from clive.db.register import make_reservation
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

        # 登録
        batchs = get_booked_batchs(session.person_id)
        sid2ary = make_sid2ary(batchs, SCANNER_IDS, DAYS_SCHEDULE)
        result = make_reservation(values, sid2ary, batchs)

        year, month, day, hour = self._get_dt()
        return render.exp_reg('exp_reg', result, year, month, day, hour)
        
    def _get_dt(self): 
        now = datetime.datetime.now()
        return now.year, now.month, now.day, now.hour


class Expregdko:
    """
    実験を登録する

    sid2aryは scanner ID毎のnumpy arrayである
    スキャナーの使用状況を管理（mapping）するためのもの
    """

    def GET(self):
        check_login()
        year, month, day, hour = self._get_dt()
        return render.exp_reg_dko('exp_reg_dko', '', year, month, day, hour)

    def POST(self):
        # inputの整形
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

        # 登録
        batchs = get_booked_batchs(session.person_id)
        sid2ary = make_sid2ary(batchs, SCANNER_IDS, DAYS_SCHEDULE)
        result = make_reservation(values, sid2ary, batchs)

        year, month, day, hour = self._get_dt()
        return render.exp_reg_dko('exp_reg_dko', '', result, year, month, day, hour)
        
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
        batchs = get_booked_batchs(session.person_id)
        return render.reg_manage(self.title, 
            self.get_html_booktable(batchs),
            self.get_html_calender(batchs))

    def POST(self):
        inputs = web.input()
        batchs = get_booked_batchs(session.person_id)
        batch = [i for i in batchs if i.id == int(inputs.batchid_rm)][0]
        cancel_batch(batch)
        # cancelした情報を反映するために再度登録batchを読みこむ
        batchs = get_booked_batchs(session.person_id)
        return render.reg_manage(self.title, 
            self.get_html_booktable(batchs), 
            self.get_html_calender(batchs))

    def get_html_booktable(self, batchs):
        return get_html_booktable(batchs, Person(session.person_id))
        
    def get_html_calender(self, batchs):
        sid2ary = make_sid2ary(batchs, SCANNER_IDS, DAYS_SCHEDULE)
        return make_calender(batchs, sid2ary)
    


from clive.db.search import get_booked_batchs
from clive.db.control import start_batch, abort_batch
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
        
        batchs = get_booked_batchs(session.person_id)
        if btype == "start":
            batch = [i for i in batchs if i.id == int(ind)][0]
            start_batch(batch)
        if btype == "abort":
            batch = [i for i in batchs if i.id == int(ind)][0]
            abort_batch(batch)
        return render.monitor(self.title,
                    self.get_scanstatus(), self.get_button())
    
    def get_scanstatus(self):
        scanners = [Scanner(i) for i in SCANNER_IDS]
        return get_html_scanstatus(scanners)
    
    def get_button(self):
        batchs = get_booked_batchs(session.person_id)
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

