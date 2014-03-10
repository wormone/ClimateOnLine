# -*- coding: utf-8 -*-
''' 常量和通用函数，调用方式如下：
    from myfunctions import station,stationNo,stationName,stationNamelong,DATAPATH,\
                            isleapyear,days36x,myrecodefile_utf8togbk,myplot
'''

###################################### 台站信息 ######################################
meta = [
"蓟县,54428",
"宝坻,54525",
"武清,54523",
"宁河,54529",
"静海,54619",
"西青,54527",
"北辰,54528",
"市区,54517",
"东丽,54526",
"津南,54622",
"大港,54645",
"汉沽,54530",
"塘沽,54623",
"全市平均,99999"
]


###################################### 台站处理 ######################################
''' 定义函数 '''
def myStation(meta):
    station = {} # 字典
    stationName = range(len(meta)) # 列表
    stationNo = range(len(meta)) # 列表
    for i,v in enumerate(meta):
        v = v.split(',')
        stationName[i] = v[0]
        stationNo[i] = v[1]
        station = dict(station,**{v[0]:v[1]})
    stationNamelong = ','.join(stationName)
    return station,stationName,stationNo,stationNamelong
# 调用生成台站变量
station,stationName,stationNo,stationNamelong = myStation(meta)


###################################### 数据路径 ######################################
''' 定义函数 '''
def myDatapath():
    import os
    if os.name == 'nt':
        DATAPATH = r"\\10.226.110.225\qhzl\Afiles"
        myfontfile = r'C:\WINDOWS.0\Fonts\msyh.ttf'
    elif os.name == 'posix':
        DATAPATH = "/mnt/225Afiles"
        myfontfile = '/usr/share/fonts/msyh/msyh.ttf'
    return DATAPATH,myfontfile
# 调用生成数据路径
DATAPATH,myfontfile = myDatapath()


###################################### 常量配置 ######################################
''' 定义 redis 连接 '''
def myRedis():
    import redis
    r = redis.StrictRedis(host="localhost", password='barfoo', port=6379, db=0)
    return r

''' 定义设置路径的函数 '''
def myPaths():
    import os
    if os.name == 'nt':
        home_path = r'D:\mytornado'
    elif os.name == 'posix':
        home_path = r'/home/oracle/mytornado/'
    static_path = os.path.join(home_path, 'static')
    template_path = os.path.join(home_path, 'templates')
    return home_path,static_path,template_path

''' 定义设置 cookie_secret 的函数 '''
def myCookie_Secret():
    import base64
    import uuid
    cookie_secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
    #cookie_secret = 'rxFWH8DlSj6E8R9ccKxJDLvLwABFjkQjmyuMQ+T23qY='
    return cookie_secret


###################################### 通用函数 ######################################
def days36x(year):
    ''' 定义常用函数，根据 year 取 days366 或 days365
        调用方式如：daysfit = days36x(year)
    '''
    days365 = [31,28,31,30,31,30,31,31,30,31,30,31]
    days366 = [31,29,31,30,31,30,31,31,30,31,30,31]
    if isleapyear(year):
        daysfit = days366
    else:
        daysfit = days365
    return daysfit


def isleapyear(year):
    ''' 定义判断是否闰年的函数 isleapyear
        t = isleapyear(2000) 返回 t = 1
        t = isleapyear(2013) 返回 t = 0
    '''
    import numpy as np
    year = int(year)
    if np.mod(year,4)==0:
        if np.mod(year,100)==0:
            if np.mod(year,400)==0:
                t = 1
            else:
                t = 0
        else:
            t = 1
    else:
        t = 0
    t = int(t)
    return t


def myrecodefile_utf8togbk(filename):
    ''' 将 utf-8 编码的文件转换为 ansi 编码 '''
    try:
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        with open(filename) as f:
            a = f.read()
            a = a.encode('gbk')
        with open(filename,'w') as f:
            f.write(a)
    except:
        print 'Wrong, nothing done.'


def myjulianday366(month,day):
    ''' 计算闰年中某月某日的儒略日，如：
        s = myulianday366(2,29)
        将得到 s = 60
        n = [31,29,31,30,31,30,31,31,30,31,30,31]
        m = range(12)
        for i in m:
        m[i] = sum(n[:i])
    '''
    m = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    s = day + m[month-1]
    return s

import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import plot,bar,xlabel,ylabel,xticks,yticks,title,savefig,clf
def myplot(x,y,Shape,Line,Color,Data,labelx,labely,tt,userplot):
    ''' 定义绘图函数 myplot
        x 和 y 分别是 X 轴和 Y 轴值
        Shape  Line  Color  Data  是绘图属性控制
        labelx 和 labely 分别是坐标轴标签
        tt 是 title
        userplot 是保存图片的全路径文件名，如 'a.png'
    '''
    ''' 常量设定，包括 myfontfile  myfont  myfontsize '''
    # 中文字体文件和字号设置
    #myfontfile = r'C:\WINDOWS.0\Fonts\msyh.ttf'
    myfontsize = 14
    # 线状、颜色和标记
    myline = {"solid":'-',"dashed":'--',"dotted":':',"none":'',"dashdot":'-.'}
    mycolor = {"k":'k',"b":'b',"r":'r',"none":'w',"g":'g',"c":'c',"y":'y',"m":'m'}
    mydata = {"dot":'.',"circle":'o',"star":'*',"none":'',"square":'s',"triangle_up":'^',\
              "triangle_down":'v',"plus":'+',"x":"x"}
    L = myline.get(Line)
    C = mycolor.get(Color)
    D = mydata.get(Data)
    # 折线图 or 柱状图
    if Shape == 'plot':
        plot(x,y,C+D+L)
    if Shape == 'bar':
        bar(x,y,width=0.6,align='center',color=C,linewidth=0)
    # 图形属性设定，打印名为 userplot 的出 PNG 格式图片
    myfont = matplotlib.font_manager.FontProperties(fname=myfontfile,size=myfontsize)
    xlabel(labelx.decode("utf8"),fontproperties=myfont)
    ylabel(labely.decode("utf8"),fontproperties=myfont)
    title(tt.decode("utf8"),fontproperties=myfont)
    xticks(fontsize=myfontsize)
    yticks(fontsize=myfontsize)
    savefig(userplot)
    clf()

###################################### 到此为止 ######################################
