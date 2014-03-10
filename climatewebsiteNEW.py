# -*- coding: utf8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.web
import redis
import time
from datetime import datetime
import os
import re
import numpy as np

################################################################ 载入编写的模块
from myfunctions import *
from weather import *
from temperature import *
from precipitation import *
from humidity import *
from windspeed import *
from sunshine import *

################################################################ 常量设定
''' 以下函数定义于 myfunctions.py '''
# 设置 redis 连接
r = myRedis()
# 设置 cookie 密码
cookie_secret = myCookie_Secret()
# 设置路径
home_path,static_path,template_path = myPaths()
# 设定本站端口
MYPORT = 6353

################################################################ 定义复用函数
''' 定义 MYget(self,THEhtmltile,THEelement)
    用于各要素页面的初始化，即被每个 class 子类的 GET 方法引用
    事实上这里的参数 THEhtmlfile 和 THEelement 被传递给 self.render 方法
    引用方式如 MYget(self,"weather.html",weather.keys())
'''
def MYget(self,THEhtmlfile,THEelement):
    try:
        #检查登陆状态
        username = self.get_secure_cookie("username")
        username = r.lindex("username",int(username))
    except redis.exceptions.ConnectionError:
        #连接不上 redis 的话，返回首页
        self.redirect('/')
    except TypeError:
        #没有用户的话，username=''，提请登陆
        self.redirect('/')
    else:
        startyear = startmonth = startday = endyear = endmonth = endday = ''
        labelx = labely = ''
        hint = ' . . .'
        userplotfile,usercsvfile = 'sample.png','sample.txt'
        self.render(THEhtmlfile,MYelement=THEelement,\
                    username=username,stationName=stationName,\
                    startyear=startyear,startmonth=startmonth,startday=startday,\
                    endyear=endyear,endmonth=endmonth,endday=endday,\
                    labelx=labelx,labely=labely,\
                    userplot=userplotfile,userfile=usercsvfile,hint=hint)

''' 定义 MYargument_get(self)
    从用户提交的表单获取所有数据，并验证表单
    引用方式很长，因为返回的变量很多：
    username,site,element,startyear,startmonth,startday,\
    endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
    hint,userplotfile,usercsvfile,thestartdate,theenddate = MYargument_get(self)
'''
def MYargument_get(self):
    # 获取用户登陆信息
    username = self.get_secure_cookie("username")
    username = r.lindex("username",int(username))
    # 获取要素、站点、月季年、坐标轴标签，注意中文编码
    element,site,period,labelx,labely = \
        [self.get_argument(k).encode('utf-8') for k in ['element','site','period','labelx','labely']]
    # 获取起止日期
    startyear,startmonth,startday,endyear,endmonth,endday = \
        [self.get_argument(k) for k in ['startyear','startmonth','startday','endyear','endmonth','endday']]
    # 获取绘图选项
    Shape,Line,Color,Data = [self.get_argument(k) for k in ['Shape','Line','Color','Data']]
    if period != "please":
        startday = 1
        try:
            # 单月份
            startmonth = endmonth = int(period)
        except ValueError:
            # 季节或全年
            season = {"冬季":[12,2],"春季":[3,5],"夏季":[6,8],"秋季":[9,11],"全年":[1,12]}
            startmonth,endmonth = season.get(period)
        days365 = [31,28,31,30,31,30,31,31,30,31,30,31]
        endday = days365[endmonth-1]
    # 首先假定输入有误，因此先设定输出为示例文件
    hint = ''
    userplotfile,usercsvfile = 'sample.png','sample.txt'
    # 所有输出项都要检查是否会被输出，是否需要提前设定
    thestartdate = theenddate = ''
    # 开始验证表单
    try:
        startyear,startmonth,startday,endyear,endmonth,endday = \
            [int(i) for i in [startyear,startmonth,startday,endyear,endmonth,endday]]
        # datetime 函数若出现 ValueError 则表明日期输入错误
        thestartdate = datetime(startyear,startmonth,startday)
        theenddate = datetime(endyear,endmonth,endday)
    except ValueError:
        hint = '未正确设置日期:-('
    else:
        if startyear < 1951:
            hint = '起始年份不能早于 1951'
        elif endyear > int(time.strftime('%Y')):
            hint = '终止日期不能超出 ' + time.strftime('%Y')
        elif startyear > endyear:
            hint = '起始年份不能晚于截止年份'
        elif site=='please' or element=='please':
            hint = '请重新选择站点和要素'
    # 返回所有获取的数据
    return username,site,element,startyear,startmonth,startday,\
            endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
            hint,userplotfile,usercsvfile,thestartdate,theenddate

''' 定义函数 MYprecal(username)
    计算开始之前调用执行的脚本，调用方式如下：
    t1,usercsvfile,userfile = MYprecal(username)
    返回时间记录 t1，文件名 usercsvfile，全路径文件名 userfile
    并打印计算开始工作的信息
'''
def MYprecal(username):
    t1 = datetime.now()
    usercsvfile = username + t1.strftime('%Y%m%d%H%M%S%f')+'.csv'
    userfile = os.path.join(static_path, usercsvfile)
    print('Working at ' + usercsvfile)
    # 返回时间记录 t1，文件名 usercsvfile，全路径文件名 userfile
    return t1,usercsvfile,userfile

''' 定义函数 MYaftercal
    计算结束后被调用执行的脚本，调用方式如下：
    输入的变量是一大堆啊，返回的是 hint 和 userplotfile：
    hint,userplotfile = MYaftercal(username,userfile,usercsvfile,t1,\
                                   startyear,endyear,site,element,thestartdate,theenddate,\
                                   y,data,Shape,Line,Color,Data,labelx,labely)
'''
def MYaftercal(username,userfile,usercsvfile,t1,\
               startyear,endyear,site,element,thestartdate,theenddate,\
               y,data,Shape,Line,Color,Data,labelx,labely):
    # 转换文件编码
    myrecodefile_utf8togbk(userfile)
    # 用户产生的图形文件也以“用户名”开头，接着是产生时间
    # 记录计算结束时间 t2
    t2 = datetime.now()
    print('Finish ' + usercsvfile + ' in ' + str(t2-t1))
    hint = ' Done in ' + str(t2-t1)[2:]
    userplotfile = username + t2.strftime('%Y%m%d%H%M%S%f')+'.png'
    userplot = os.path.join(static_path, userplotfile)
    # 图标题为年限站点要素（月-日至月-日）
    tt = str(startyear)+"-"+str(endyear) + site + element +\
         "（" + thestartdate.strftime("%m-%d") + "至" + theenddate.strftime("%m-%d") + "）"
    # 开始绘图
    myplot(y,data,Shape,Line,Color,Data,labelx,labely,tt,userplot)
    return hint,userplotfile


################################################################ 以下编写 class 并配置 url
''' 主页 '''
class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        #设定初始状态：t,username,status,passwd
        passwd,status = '','请登录'
        try:
            #检查登陆状态，获取 cookies 并连接 redis
            username = self.get_secure_cookie("username")
            username = r.lindex("username",int(username))
        except redis.exceptions.ConnectionError:
            #连接不上 redis 的话
            t,status = False,"用户数据库已关闭:-("
        except TypeError:
            #没有用户的话，username=''，提请登陆
            t,username = False,''
        else:
            #用户已登录，username 已存在，表示欢迎
            t = True
        #变量都已设定，最后执行网页渲染
        self.render('home.html',t=t,username=username,status=status,passwd=passwd)

    def post(self):
        try:
            #检查登陆状态，获取 cookies 并连接 redis
            username = self.get_secure_cookie("username")
            username = r.lindex("username",int(username))
        except redis.exceptions.ConnectionError:
            #连接不上 redis 的话
            t,passwd,status = False,'','用户数据库已关闭:-('
        except TypeError:
            #没有已登录用户的话，验证用户输入的用户名和密码
            username,passwd = [self.get_argument(k) for k in ['username','passwd']]
            try:
                a = [(m, n) for m, n in enumerate(r.lrange("username", 0, -1)) if n == username ]
                a[0][0]
                # a[0][0] 是 username 对应的 passwd 索引
            except IndexError:
                #用户名不存在
                t,passwd,status = False,'','用户不存在:-('
            except redis.exceptions.ConnectionError:
                #连接不上 redis
                t,passwd,status = False,'','用户数据库已关闭:-('
            else:
                #用户名存在，验证密码
                if r.lindex("passwd", a[0][0]) == passwd:
                    #密码正确，设置 cookie 有效期为 1 天
                    self.set_secure_cookie("username", str(a[0][0]), expires_days=1)
                    t,status = True,''
                    print(username+' logIN from '+self.request.remote_ip+' at '+time.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    #密码错误
                    t,status = False,'密码错误:-('
        else:
            #用户已登录的话，现在要执行退出
            print(username+' logOUT from '+self.request.remote_ip+' at '+time.strftime('%Y-%m-%d %H:%M:%S'))
            self.clear_cookie("username")
            t,passwd,status = False,'','已退出'
        #变量都已设定，最后执行网页渲染
        self.render('home.html',t=t,username=username,status=status,passwd=passwd)

''' 用户 '''
class UserHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            username = self.get_secure_cookie("username")
            username = r.lindex("username",int(username))
        except (TypeError,redis.exceptions.ConnectionError):
            self.redirect('/')
        else:
            a = [m for m, n in enumerate(r.lrange("username", 0, -1)) if n == username]
            role,name,panel = [r.lindex(k,a[0]) for k in ['role','name','panel']]
            message = '更改后请退出重新登录'
            oldpass = newpass1 = newpass2 = ''
            self.render('user.html',username=username,name=name,role=role,panel=panel,message=message,\
                        oldpass=oldpass,newpass1=newpass1,newpass2=newpass2)

    def post(self):
        try:
            username = self.get_secure_cookie("username")
            username = r.lindex("username",int(username))
        except (TypeError,redis.exceptions.ConnectionError):
            self.redirect('/')
        else:
            a = [m for m, n in enumerate(r.lrange("username", 0, -1)) if n == username]
            role,name,panel = [r.lindex(k,a[0]) for k in ['role','name','panel']]
            oldpass,newpass1,newpass2 = [self.get_argument(k) for k in ['oldpass','newpass1','newpass2']]
            if oldpass == '':
                message = '请输入旧密码'
            elif oldpass != r.lindex('passwd',a[0]):
                message = '旧密码输入错误'
            elif newpass1 == '':
                message = '请输入新密码'
            elif not re.match(r'^[0-9a-zA-Z]{2,10}$',newpass1):
                message = '只允许2-10位的数字字母'
            elif newpass2 == '':
                message = '请再次输入新密码'
            elif newpass2 != newpass1:
                message = '两次输入不一致'
            else:
                r.lset('passwd',a[0],newpass2)
                r.save()
                print(username+' changes password at '+time.strftime('%Y-%m-%d %H:%M:%S'))
                message = '已更新，下次登录请使用新密码 :-)'
            self.render('user.html',username=username,name=name,role=role,panel=panel,message=message,\
                        oldpass=oldpass,newpass1=newpass1,newpass2=newpass2)

''' 管理员 '''
class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            username = self.get_secure_cookie("username")
            username = r.lindex("username",int(username))
        except (TypeError,redis.exceptions.ConnectionError):
            self.redirect('/')
        else:
            a = [m for m, n in enumerate(r.lrange("username", 0, -1)) if n == username]
            myrole = r.lindex('role',a[0])
            user = name = role = panel = pwd = ''
            message = ''
            self.render('admin.html',username=username,\
                        user=user,name=name,role=role,panel=panel,pwd=pwd,message=message)

    def post(self):
        try:
            username = self.get_secure_cookie("username")
            username = r.lindex("username",int(username))
        except (TypeError,redis.exceptions.ConnectionError):
            self.redirect('/')
        else:
            a = [m for m, n in enumerate(r.lrange("username", 0, -1)) if n == username]
            myrole = r.lindex('role',a[0])
            user = name = role = panel = pwd = ''
            message = '对不起，普通用户不能操作 :-('
            # 管理员才能执行以下操作
            if myrole == '1':
                # 获取用户输入
                user,pwd,cmd = [self.get_argument(k) for k in ['user','pwd','cmd']]
                role,name,panel = [self.get_argument(k).encode('utf8') for k in ['role','name','panel']]
                role = {'普通用户':'0','管理员':'1'}.get(role)
                # 验证表单和操作执行
                if cmd == "please":
                    message = '请选择操作'
                elif cmd == "search":
                    if user == '':
                        message = '请输入用户名'
                    else:
                        c = r.lrange("username", 0, -1).count(user)
                        if c == 0:
                            message = '用户不存在'
                            name = role = panel = pwd = ''
                        elif c == 1:
                            a = [m for m, n in enumerate(r.lrange("username", 0, -1)) if n == user]
                            name,role,panel,pwd = [r.lindex(k,a[0]) for k in ['name','role','panel','passwd']]
                            message = '查询完毕'
                elif cmd == "register":
                    c = r.lrange("username", 0, -1).count(user)
                    if c == 1:
                        message = '用户名已存在 :-('
                    elif name == '' or role == '' or panel == '' or pwd == '':
                        message = '信息填写不全'
                    elif not re.match(r'^[0-9a-zA-Z]{2,20}$',user):
                        message = '用户名只允许2-20位的数字字母'
                    elif not re.match(r'^[0-9a-zA-Z]{2,10}$',pwd):
                        message = '密码只允许2-10位的数字字母'
                    elif role != '0' and role != '1':
                        message = '用户类型只能是“普通用户”或“管理员”'
                    elif not re.match(ur"[\u4e00-\u9fa5]+",name.decode('utf8')):
                        message = '姓名只允许中文'
                    elif not re.match(ur"[\u4e00-\u9fa5]+",panel.decode('utf8')):
                        message = '单位只允许中文'
                    else:
                        p = r.pipeline()
                        for i in [['username',user],['passwd',pwd],['name',name],['panel',panel],['role',role]]:
                            p.rpush(i[0],i[1])
                        p.execute()
                        r.save()
                        message = '已注册用户 ' + user
                elif cmd == "delete":
                    c = r.lrange("username", 0, -1).count(user)
                    if c == 0:
                        message = '用户不存在 :-('
                    elif c == 1:
                        x = 'to be removed'
                        a = [m for m, n in enumerate(r.lrange("username", 0, -1)) if n == user]
                        p = r.pipeline()
                        for i in ['username','passwd','name','panel','role']:
                            p.lset(i,a[0],x).lrem(i,0,x)
                        p.execute()
                        r.save()
                        message = '已删除用户 ' + user
                        user = name = role = panel = pwd = ''
            self.render('admin.html',username=username,\
                        user=user,name=name,role=role,panel=panel,pwd=pwd,message=message)

''' 天气现象 '''
class WeatherHandler(tornado.web.RequestHandler):
    def get(self):
        # 调用自定义的 MYget 函数
        ###################### 设定常量 #########################
        MYget(self,"weather.html",weather.keys())
        ###################### 结束设定 #########################
    def post(self):
        try:
            # 调用自定义的 MYargument_get 函数，返回所有变量
            username,site,element,startyear,startmonth,startday,\
            endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
            hint,userplotfile,usercsvfile,thestartdate,theenddate = MYargument_get(self)
        except redis.exceptions.ConnectionError:
            self.redirect('/')
        else:
            # 如果 hint == '' 即表明输入正确，可以进行计算
            if hint == '':
                # 调用自定义的 MYprecal 函数
                t1,usercsvfile,userfile = MYprecal(username)
                ###############################################> 计算过程开始 <###############################################
                weathercode = weather.get(element)
                element = element+"日数" # 注意这里在天气现象名称后加了日数，传给 MYaftercal 函数
                if site == "全市平均":
                    # 全市平均
                    y,z,data = myreadaW0paraM(startyear,endyear,startmonth,endmonth,startday,endday,weathercode)
                    t = np.transpose(np.vstack((y,z,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%5.1f",header="年份,"+stationNamelong,delimiter=",")
                else:
                    # 单站
                    stationnumber = station.get(site)
                    y,data = myreadaW0para(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,weathercode)
                    t = np.transpose(np.vstack((y,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%5.1f",header="年份,"+site,delimiter=",")
                ###############################################> 计算过程结束 <###############################################
                # 调用自定义的 MYaftercal 函数
                hint,userplotfile = MYaftercal(username,userfile,usercsvfile,t1,\
                                               startyear,endyear,site,element,thestartdate,theenddate,\
                                               y,data,Shape,Line,Color,Data,labelx,labely)
            ###################### 最后渲染 HTML 页面 ######################
            self.render("weather.html",MYelement=weather.keys(),\
                        username=username,stationName=stationName,\
                        startyear=startyear,startmonth=startmonth,startday=startday,\
                        endyear=endyear,endmonth=endmonth,endday=endday,\
                        labelx=labelx,labely=labely,\
                        userplot=userplotfile,userfile=usercsvfile,hint=hint)

''' 气温 '''
class TemperatureHandler(tornado.web.RequestHandler):
    def get(self):
        # 调用自定义的 MYget 函数
        ###################### 设定常量 #########################
        MYget(self,"temperature.html",temperature)
        ###################### 结束设定 #########################
    def post(self):
        try:
            # 调用自定义的 MYargument_get 函数，返回所有变量
            username,site,element,startyear,startmonth,startday,\
            endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
            hint,userplotfile,usercsvfile,thestartdate,theenddate = MYargument_get(self)
        except redis.exceptions.ConnectionError:
            self.redirect('/')
        else:
            # 如果 hint == '' 即表明输入正确，可以进行计算
            if hint == '':
                # 调用自定义的 MYprecal 函数
                t1,usercsvfile,userfile = MYprecal(username)
                ###############################################> 计算过程开始 <###############################################
                paraT = {'平均气温':['tm','mean'],\
                         '平均最高气温':['tx','mean'],\
                         '平均最低气温':['tn','mean'],\
                         '极端最高气温':['tx','max'],\
                         '极端最低气温':['tn','min']}
                paraTdays = {'35度以上高温日数':['tx',35,'gt'],\
                              '-10度以下低温日数':['tn',-10,'lt']}
                paraTsum = {'0度以上活动积温':[0,'gt'],\
                            '10度以上活动积温':[10,'gt'],\
                            '0度以下负积温':[0,'lt']}
                # 从字典中找 key 的 value，找不到就是 None
                paraT,paraTdays,paraTsum = [k.get(element) for k in [paraT,paraTdays,paraTsum]]
                if site == "全市平均":
                    # 全市平均，注意函数名有 M，变量中没有 stationnumber，返回值有 z
                    if paraT:
                        tmtxtn,MMM = paraT
                        y,z,data = myreadaTM(startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,MMM)
                    elif paraTdays:
                        tmtxtn,threshold,method = paraTdays
                        y,z,data = myreadaTdaysM(startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,threshold,method)
                    elif paraTsum:
                        threshold,method = paraTsum
                        y,z,data = myreadaTsumM(startyear,endyear,startmonth,endmonth,startday,endday,threshold,method)
                    t = np.transpose(np.vstack((y,z,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+stationNamelong,delimiter=",")
                else:
                    # 单站
                    stationnumber = station.get(site)
                    if paraT:
                        tmtxtn,MMM = paraT
                        y,data = myreadaT(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,MMM)
                    elif paraTdays:
                        tmtxtn,threshold,method = paraTdays
                        y,data = myreadaTdays(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,threshold,method)
                    elif paraTsum:
                        threshold,method = paraTsum
                        y,data = myreadaTsum(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,threshold,method)
                    t = np.transpose(np.vstack((y,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+site,delimiter=",")
                ###############################################> 计算过程结束 <###############################################
                # 调用自定义的 MYaftercal 函数
                hint,userplotfile = MYaftercal(username,userfile,usercsvfile,t1,\
                                               startyear,endyear,site,element,thestartdate,theenddate,\
                                               y,data,Shape,Line,Color,Data,labelx,labely)
            ###################### 最后渲染 HTML 页面 ######################
            self.render("temperature.html",MYelement=temperature,\
                        username=username,stationName=stationName,\
                        startyear=startyear,startmonth=startmonth,startday=startday,\
                        endyear=endyear,endmonth=endmonth,endday=endday,\
                        labelx=labelx,labely=labely,\
                        userplot=userplotfile,userfile=usercsvfile,hint=hint)


''' 降水 '''
class PrecipitationHandler(tornado.web.RequestHandler):
    def get(self):
        # 调用自定义的 MYget 函数
        ###################### 设定常量 #########################
        MYget(self,"precipitation.html",precipitation)
        ###################### 结束设定 #########################
    def post(self):
        try:
            # 调用自定义的 MYargument_get 函数，返回所有变量
            username,site,element,startyear,startmonth,startday,\
            endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
            hint,userplotfile,usercsvfile,thestartdate,theenddate = MYargument_get(self)
        except redis.exceptions.ConnectionError:
            self.redirect('/')
        else:
            # 如果 hint == '' 即表明输入正确，可以进行计算
            if hint == '':
                # 调用自定义的 MYprecal 函数
                t1,usercsvfile,userfile = MYprecal(username)
                ###############################################> 计算过程开始 <###############################################
                para = {'累计降水量':[0,99999,'sum'],\
                        '日降水量大于等于0.1mm日数':[0,99999,'days'],\
                        '日降水量大于等于1mm日数':[0.9,99999,'days'],\
                        '小雨日数':[0,10,'days'],\
                        '中雨日数':[9.9,25,'days'],\
                        '大雨日数':[24.9,50,'days'],\
                        '暴雨日数':[49.9,99999,'days']}
                above,below,daysorsum = para.get(element)
                if site == "全市平均":
                    # 全市平均，注意函数名有 M，变量中没有 stationnumber，返回值有 z
                    y,z,data = myreadaRM(startyear,endyear,startmonth,endmonth,startday,endday,above,below,daysorsum)
                    # 降水的单位是毫米，日数的单位是天
                    t = np.transpose(np.vstack((y,z,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+stationNamelong,delimiter=",")
                else:
                    # 单站
                    stationnumber = station.get(site)
                    y,data = myreadaR(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,above,below,daysorsum)
                    # 降水的单位是毫米，日数的单位是天
                    t = np.transpose(np.vstack((y,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+site,delimiter=",")
                ###############################################> 计算过程结束 <###############################################
                # 调用自定义的 MYaftercal 函数
                hint,userplotfile = MYaftercal(username,userfile,usercsvfile,t1,\
                                               startyear,endyear,site,element,thestartdate,theenddate,\
                                               y,data,Shape,Line,Color,Data,labelx,labely)
            ###################### 最后渲染 HTML 页面 ######################
            self.render("precipitation.html",MYelement=precipitation,\
                        username=username,stationName=stationName,\
                        startyear=startyear,startmonth=startmonth,startday=startday,\
                        endyear=endyear,endmonth=endmonth,endday=endday,\
                        labelx=labelx,labely=labely,\
                        userplot=userplotfile,userfile=usercsvfile,hint=hint)

''' 相对湿度 '''
class HumidityHandler(tornado.web.RequestHandler):
    def get(self):
        # 调用自定义的 MYget 函数
        ###################### 设定常量 #########################
        MYget(self,"humidity.html",humidity)
        ###################### 结束设定 #########################
    def post(self):
        try:
            # 调用自定义的 MYargument_get 函数，返回所有变量
            username,site,element,startyear,startmonth,startday,\
            endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
            hint,userplotfile,usercsvfile,thestartdate,theenddate = MYargument_get(self)
        except redis.exceptions.ConnectionError:
            self.redirect('/')
        else:
            # 如果 hint == '' 即表明输入正确，可以进行计算
            if hint == '':
                # 调用自定义的 MYprecal 函数
                t1,usercsvfile,userfile = MYprecal(username)
                ###############################################> 计算过程开始 <###############################################
                MMM = {'平均相对湿度':'mean','平均最小相对湿度':'meanmin','最小相对湿度最小值':'minmin'}.get(element)
                if site == "全市平均":
                    # 全市平均，注意函数名有 M，变量中没有 stationnumber，返回值有 z
                    y,z,data = myreadaRHM(startyear,endyear,startmonth,endmonth,startday,endday,MMM)
                    t = np.transpose(np.vstack((y,z,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+stationNamelong,delimiter=",")
                else:
                    # 单站
                    stationnumber = station.get(site)
                    y,data = myreadaRH(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,MMM)
                    t = np.transpose(np.vstack((y,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+site,delimiter=",")
                ###############################################> 计算过程结束 <###############################################
                # 调用自定义的 MYaftercal 函数
                hint,userplotfile = MYaftercal(username,userfile,usercsvfile,t1,\
                                               startyear,endyear,site,element,thestartdate,theenddate,\
                                               y,data,Shape,Line,Color,Data,labelx,labely)
            ###################### 最后渲染 HTML 页面 ######################
            self.render("humidity.html",MYelement=humidity,\
                        username=username,stationName=stationName,\
                        startyear=startyear,startmonth=startmonth,startday=startday,\
                        endyear=endyear,endmonth=endmonth,endday=endday,\
                        labelx=labelx,labely=labely,\
                        userplot=userplotfile,userfile=usercsvfile,hint=hint)

''' 风速风向 '''
class WindspeedHandler(tornado.web.RequestHandler):
    def get(self):
        # 调用自定义的 MYget 函数
        ###################### 设定常量 #########################
        MYget(self,"windspeed.html",windspeed)
        ###################### 结束设定 #########################
    def post(self):
        try:
            # 调用自定义的 MYargument_get 函数，返回所有变量
            username,site,element,startyear,startmonth,startday,\
            endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
            hint,userplotfile,usercsvfile,thestartdate,theenddate = MYargument_get(self)
        except redis.exceptions.ConnectionError:
            self.redirect('/')
        else:
            # 如果 hint == '' 即表明输入正确，可以进行计算
            if hint == '':
                # 调用自定义的 MYprecal 函数
                t1,usercsvfile,userfile = MYprecal(username)
                ###############################################> 计算过程开始 <###############################################
                MMM = {'平均风速':'mean','平均最大风速':'meanmax','最大风速最大值':'maxmax'}.get(element)
                if site == "全市平均":
                    # 全市平均，注意函数名有 M，变量中没有 stationnumber，返回值有 z
                    y,z,data = myreadaFM(startyear,endyear,startmonth,endmonth,startday,endday,MMM)
                    t = np.transpose(np.vstack((y,z,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+stationNamelong,delimiter=",")
                else:
                    # 单站
                    stationnumber = station.get(site)
                    y,data = myreadaF(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,MMM)
                    t = np.transpose(np.vstack((y,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+site,delimiter=",")
                ###############################################> 计算过程结束 <###############################################
                # 调用自定义的 MYaftercal 函数
                hint,userplotfile = MYaftercal(username,userfile,usercsvfile,t1,\
                                               startyear,endyear,site,element,thestartdate,theenddate,\
                                               y,data,Shape,Line,Color,Data,labelx,labely)
            ###################### 最后渲染 HTML 页面 ######################
            self.render("windspeed.html",MYelement=windspeed,\
                        username=username,stationName=stationName,\
                        startyear=startyear,startmonth=startmonth,startday=startday,\
                        endyear=endyear,endmonth=endmonth,endday=endday,\
                        labelx=labelx,labely=labely,\
                        userplot=userplotfile,userfile=usercsvfile,hint=hint)

''' 日照 '''
class SunshineHandler(tornado.web.RequestHandler):
    def get(self):
        # 调用自定义的 MYget 函数
        ###################### 设定常量 #########################
        MYget(self,"sunshine.html",sunshine)
        ###################### 结束设定 #########################
    def post(self):
        try:
            # 调用自定义的 MYargument_get 函数，返回所有变量
            username,site,element,startyear,startmonth,startday,\
            endyear,endmonth,endday,Shape,Line,Color,Data,labelx,labely,\
            hint,userplotfile,usercsvfile,thestartdate,theenddate = MYargument_get(self)
        except redis.exceptions.ConnectionError:
            self.redirect('/')
        else:
            # 如果 hint == '' 即表明输入正确，可以进行计算
            if hint == '':
                # 调用自定义的 MYprecal 函数
                t1,usercsvfile,userfile = MYprecal(username)
                ###############################################> 计算过程开始 <###############################################
                MMM = {'平均日照时数':'mean','累计日照时数':'sum'}.get(element)
                if site == "全市平均":
                    # 全市平均，注意函数名有 M，变量中没有 stationnumber，返回值有 z
                    y,z,data = myreadaSM(startyear,endyear,startmonth,endmonth,startday,endday,MMM)
                    t = np.transpose(np.vstack((y,z,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+stationNamelong,delimiter=",")
                else:
                    # 单站
                    stationnumber = station.get(site)
                    y,data = myreadaS(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,MMM)
                    t = np.transpose(np.vstack((y,data)))
                    t[np.isnan(t)] = 32766
                    np.savetxt(userfile,t,fmt="%10.1f",header="年份,"+site,delimiter=",")
                ###############################################> 计算过程结束 <###############################################
                # 调用自定义的 MYaftercal 函数
                hint,userplotfile = MYaftercal(username,userfile,usercsvfile,t1,\
                                               startyear,endyear,site,element,thestartdate,theenddate,\
                                               y,data,Shape,Line,Color,Data,labelx,labely)
            ###################### 最后渲染 HTML 页面 ######################
            self.render("sunshine.html",MYelement=sunshine,\
                        username=username,stationName=stationName,\
                        startyear=startyear,startmonth=startmonth,startday=startday,\
                        endyear=endyear,endmonth=endmonth,endday=endday,\
                        labelx=labelx,labely=labely,\
                        userplot=userplotfile,userfile=usercsvfile,hint=hint)

''' settings '''
settings = {
    "static_path":static_path,
    "template_path":template_path,
    "cookie_secret":cookie_secret,
    "xsrf_cookies":True,
}

''' app '''
app = tornado.web.Application([
    (r"/",HomeHandler),
    (r"/user",UserHandler),
    (r"/admin",AdminHandler),
    (r"/weather",WeatherHandler),
    (r"/temperature",TemperatureHandler),
    (r"/precipitation",PrecipitationHandler),
    (r"/humidity",HumidityHandler),
    (r"/windspeed",WindspeedHandler),
    (r"/sunshine",SunshineHandler),
],**settings)

''' MYPORT 须已设定 '''
if __name__ == '__main__':
    sockets = tornado.netutil.bind_sockets(MYPORT)
    if os.name == 'posix':
        tornado.process.fork_processes(0) # 0 表示按 CPU 数目创建相应数目的子进程
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()
