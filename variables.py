# -*- coding: utf8 -*-
import re
import os
import numpy as np
from myfunctions import days36x

''' variables.py 说明：
    包含了单个 A0 或 A 文件读取降水、气温、风速、湿度、日照的函数，
    返回的数值全部为整数，缺测以 nan 表示，
    数值单位与原文件一致，即降水 0.1 毫米，气温 0.1 度，风速 0.1 米每秒，湿度 %，日照 0.1 小时
'''

# 定义常用函数，字符串整数，否则为 NaN
# 调用方式如：x = intORnan(x)
def intORnan(x):
    try:
        x = int(x)
    except ValueError:
        x = np.nan
    return x

# 定义降水编码的一个判断函数 Rdecode，调用方式如下
# x = Rdecode('dddd')
def Rdecode(x):
    if x[0] == ';':
        # 首位为 ; 号表示超过 1000.0mm
        x = 10000 + int(x[1:])*10
    if x[0] == ':':
        # 首位为 : 号表示超过 2000.0mm
        x = 20000 + int(x[1:])*10
    if x[0] == '.':
        # 首位为 . 号表示雨夹雪（首位 + 号表示雪）
        x = int(x[1:])
    if x == ',,,,':
        x = 0
    else:
        # 雾露霜记为负值，所以取相反数
        x = abs(intORnan(x))
    return x


''' 降水 '''
def R(filename):
    year = int(filename[-10:-6])
    month = int(filename[-6:-4])
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^R([^=]?)(=?)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        # X 是方式位，v 是数据记录串
        X,e,v = [i.group(k) for k in range(1,4)]
    if e == '=' or v == '0' or v == '=\n':
        # R0= 全月无降水的情况下
        # R6\n0=\n0= 也是全月无降水，如宝坻 2009 年 1 月
        # R6\n=\n= 也是全月无降水，如宝坻 2008 年 1 月
        daysfit = days36x(year)
        # 设置所有数据为 0
        d = np.zeros(daysfit[month-1])
    else:
        if X == '1' or X == '3':
            # 判断闰年与否即每月日数
            daysfit = days36x(year)
            # 设定零数组
            d = np.zeros(daysfit[month-1])
            # 前两位是降水日期，最后四位是日降水量
            reg2 = re.compile(r'^(.{2}).{11}(.{4})\n?',re.M)
            ms = reg2.finditer(v)
            for i in ms:
                t,x = [i.group(k) for k in [1,2]]
                t = int(t)
                x = Rdecode(x)
                d[t-1] = x
        elif X == '0' or X == '2' or X == '6' or X == '5':
            # 最后四位是日降水量
            reg2 = re.compile(r'^.*(.{4})\n?',re.M)
            ms = reg2.finditer(v)
            d = np.arange(0)
            for i in ms:
                x = i.group(1)
                x = Rdecode(x)
                d = np.hstack((d,x))
    return d


''' 气温 '''
### 平均气温
def T(filename):
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^T(.)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X,v = [i.group(k) for k in [1,2]]
    if X == '0':
        reg2 = re.compile(r'^(.{4}) (.{4}) (.{4}) (.{4})',re.M)
        ms = reg2.finditer(v)
    elif X == '9':
        # 修订了三次观测向四次观测的转换
        reg2 = re.compile(r'^(.{4}) (.{4}) (.{4}) (.{4}) (.{4})',re.M)
        ms = reg2.finditer(v)
    elif X == 'B':
        # 把非点号 . 结尾的换行符替换为空格，两行合并成一行，为一天
        reg2 = re.compile(r'(?<=[^\.])\n',re.M)
        v = re.sub(reg2,' ',v)
        reg2 = re.compile(r'^.{25}(.{4}).{26}(.{4}).{26}(.{4}).{26}(.{4})',re.M)
    if X == '0' or X == 'B':
        # 以下处理对于方式位 0 和 B 都是一样的
        ms = reg2.finditer(v)
        d = np.arange(0,dtype=np.float32)
        for i in ms:
            v02,v08,v14,v20 = [intORnan(i.group(k)) for k in range(1,5)]
            x = v02 + v08 + v14 + v20
            d = np.hstack((d,x))
        # 四个时次平均，保留一位小数
        d = np.rint(d/4)
    if X == '9':
        ''' 发现塘沽站1951年1月开始为三次观测 '''
        # 修订了三次观测向四次观测的转换
        ms = reg2.finditer(v)
        # 初始化为空数组
        d08 = d14 = d20 = dtn = np.arange(0,dtype=np.float32)
        for i in ms:
            v08,v14,v20,vtx,vtn = [intORnan(i.group(k)) for k in range(1,6)]
            # 定义匿名函数，追加数列
            m = lambda x:np.hstack((x[0],x[1]))
            # 用列表解析法执行重复命令
            d08,d14,d20,dtn = [m(x) for x in [[d08,v08],[d14,v14],[d20,v20],[dtn,vtn]]]
        d02 = (d20[:-1] + dtn[1:])/2
        d02 = np.hstack((np.nan,d02))
        d = np.rint((d02+d08+d14+d20)/4)
    return d


### 最高气温
def Tx(filename):
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^T(.)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X,v = [i.group(k) for k in [1,2]]
    if X == '0':
        reg2 = re.compile(r'^.{20}(.{4})',re.M)
        ms = reg2.finditer(v)
    elif X == '9':
        reg2 = re.compile(r'^.{15}(.{4})',re.M)
        ms = reg2.finditer(v)
    elif X == 'B':
        # 把非点号 . 结尾的换行符替换为空格，两行合并成一行，为一天
        reg2 = re.compile(r'(?<=[^\.])\n',re.M)
        v = re.sub(reg2,' ',v)
        reg3 = re.compile(r'^.{120}(.{4})',re.M)
        ms = reg3.finditer(v)
    # 以下处理对于方式位 0 和 B 都是一样的
    d = np.arange(0,dtype=np.float32)
    for i in ms:
        x = i.group(1)
        d = np.hstack((d,intORnan(x)))
    return d


### 最低气温
def Tn(filename):
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^T(.)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X,v = [i.group(k) for k in [1,2]]
    if X == '0':
        reg2 = re.compile(r'^.{25}(.{4})',re.M)
        ms = reg2.finditer(v)
    elif X == '9':
        reg2 = re.compile(r'^.{20}(.{4})',re.M)
        ms = reg2.finditer(v)
    elif X == 'B':
        # 把非点号 . 结尾的换行符替换为空格，两行合并成一行，为一天
        reg2 = re.compile(r'(?<=[^\.])\n',re.M)
        v = re.sub(reg2,' ',v)
        reg3 = re.compile(r'^.{130}(.{4})',re.M)
        ms = reg3.finditer(v)
    # 以下处理对于方式位 0 和 B 都是一样的
    d = np.arange(0,dtype=np.float32)
    for i in ms:
        x = i.group(1)
        d = np.hstack((d,intORnan(x)))
    return d


''' 风速 '''
### 平均风速
def F(filename):
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^F(.)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X,v = [i.group(k) for k in [1,2]]
    if X == '0' or X == '2' or X == '4':
        reg2 = re.compile(r'^.{3}(.{3}) .{3}(.{3}) .{3}(.{3}) .{3}(.{3})',re.M)
    elif X == '9' or X == '6' or X == '7':
        # 02 时无观测，之后后三个时次
        reg2 = re.compile(r'^.{3}(.{3}) .{3}(.{3}) .{3}(.{3})',re.M)
    elif X == 'N':
        reg2 = re.compile(r'^.{38}(.{3})\n.{38}(.{3})\n.{38}(.{3})\n.{38}(.{3})',re.M)
    # 注意方式位 9 6 7 的处理，是三个时次的平均
    ms = reg2.finditer(v)
    d = np.arange(0,dtype=np.float32)
    if X == '0' or X == '2' or X == '4' or X == 'N':
        for i in ms:
            v02,v08,v14,v20 = [intORnan(i.group(k)) for k in range(1,5)]
            x = v02 + v08 + v14 + v20
            d = np.hstack((d,x))
        d = np.rint(d/4)
    elif X == '9' or X == '6' or X == '7':
        for i in ms:
            v08,v14,v20 = [intORnan(i.group(k)) for k in range(1,4)]
            x = v08 + v14 + v20
            d = np.hstack((d,x))
        d = np.rint(d/3)
    return d


### 十分钟最大风速
def Fx(filename):
    year = int(filename[-10:-6])
    month = int(filename[-6:-4])
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^F(.)\n',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X = i.group(1)
    if X == '2' or X == '9':
        # 方式位为 2 或 9，没有最大风速记录
        # 判断闰年与否即每月日数
        daysfit = days36x(year)
        # 设置所有数据为 nan
        d = np.ones(daysfit[month-1])*np.nan
    elif X == '0' or X == '4' or X == '6' or X == '7':
        reg = re.compile(r'^F.(.+?(?==))(.+?(?==))',re.M+re.S)
        ms = reg.finditer(s)
        for i in ms:
            v = i.group(2)
        reg2 = re.compile(r'^(.{3})',re.M)
    elif X == 'N':
        reg = re.compile(r'^F.(.+?(?==))(.+?(?==))(.+?(?==))',re.M+re.S)
        # 第一段是逐时十分钟平均风速，第二段是逐时两分钟平均风速
        # 第三段是日最大十分钟平均风速和极大瞬时风速
        ms = reg.finditer(s)
        for i in ms:
            v = i.group(3)
        reg2 = re.compile(r'^(.{3})',re.M)
    if X == '0' or X == '4' or X == '6' or X == '7' or X == 'N' :
        ms = reg2.finditer(v)
        d = np.arange(0,dtype=np.float32)
        for i in ms:
            x = i.group(1)
            d = np.hstack((d,intORnan(x)))
    return d


''' 相对湿度 '''
### 平均相对湿度
def RH(filename):
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^U(.)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X,v = [i.group(k) for k in [1,2]]
    if X == 'B':
        # 把非点号 . 结尾的换行符替换为空格，两行合并成一行，为一天
        reg2 = re.compile(r'(?<=[^\.])\n',re.M)
        v = re.sub(reg2,' ',v)
        reg2 = re.compile(r'^.{15}(.{2}).{16}(.{2}).{16}(.{2}).{16}(.{2})',re.M)
    elif X == '0' or X == '2':
        reg2 = re.compile(r'^(.{2}) (.{2}) (.{2}) (.{2})',re.M)
    elif X == '9' or X == '7':
        reg2 = re.compile(r'(.{2}) (.{2}) (.{2})',re.M)
    if X == '9' or X == '7':
        ms = reg2.finditer(v)
        d = np.arange(0,dtype=np.float32)
        for i in ms:
            # 定义匿名函数，将 '%%' 替换为 '100'，表示相对湿度 100%
            m = lambda x:x*(x!='%%')+'100'*(x=='%%')
            v08,v14,v20 = [intORnan(m(i.group(k))) for k in range(1,4)]
            x = v08 + v14 + v20
            d = np.hstack((d,x))
        # 三个时次平均，保留一位小数
        d = np.rint(d/3)
    elif X == 'B' or X == '0' or X == '2':
        ms = reg2.finditer(v)
        d = np.arange(0,dtype=np.float32)
        for i in ms:
            # 定义匿名函数，将 '%%' 替换为 '100'，表示相对湿度 100%
            m = lambda x:x*(x!='%%')+'100'*(x=='%%')
            v02,v08,v14,v20 = [intORnan(m(i.group(k))) for k in range(1,5)]
            x = v02 + v08 + v14 + v20
            d = np.hstack((d,x))
        # 四个时次平均，保留一位小数
        d = np.rint(d/4)
    return d


### 最小相对湿度
def RHn(filename):
    year = int(filename[-10:-6])
    month = int(filename[-6:-4])
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^U(.)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X,v = [i.group(k) for k in [1,2]]
    if X == 'B':
        # 把非点号 . 结尾的换行符替换为空格，两行合并成一行，为一天
        reg2 = re.compile(r'(?<=[^\.])\n',re.M)
        v = re.sub(reg2,' ',v)
        reg2 = re.compile(r'^.{72}(.{2})',re.M)
    elif X == '0':
        reg2 = re.compile(r'.{12}(.{2})',re.M)
    elif X == '7':
        reg2 = re.compile(r'.{9}(.{2})',re.M)
    elif X == '2' or X == '9':
        # 方式位为 2 或 9，没有最小相对湿度记录
        # 判断闰年与否即每月日数
        daysfit = days36x(year)
        # 设置所有数据为 nan
        d = np.ones(daysfit[month-1])*np.nan
    if X == 'B' or X == '0' or X == '7':
        ms = reg2.finditer(v)
        d = np.arange(0,dtype=np.float32)
        for i in ms:
            x = i.group(1)
            if x == '%%':
                x = 100
            d = np.hstack((d,intORnan(x)))
    return d


''' 日照时数 '''
def S(filename):
    year = int(filename[-10:-6])
    month = int(filename[-6:-4])
    f = open(filename)
    s = f.read()
    f.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    s = re.sub(r'\r','',s)
    reg = re.compile(r'^S([^=]?)(=?)\n(.+?(?==))',re.M+re.S)
    ms = reg.finditer(s)
    for i in ms:
        X,e,v = [i.group(k) for k in range(1,4)]
    try:
        e
    except NameError:
        ''' 发现宝坻站1959年3月 S= 全月无日照记录，
            且 (.+?(?==)) 无匹配，ms 为空，X e v 都不存在 '''
        daysfit = days36x(year)
        # 设置所有数据为 nan
        d = np.ones(daysfit[month-1])*np.nan
    else:
        if e == '=' or X == '':
            ''' 市区站2013年1月开始 S= 全月无日照记录，
                但 (.+?(?==)) 有匹配，ms 不为空 '''
            # SX= 全月无日照记录的情况
            daysfit = days36x(year)
            # 设置所有数据为 nan
            d = np.ones(daysfit[month-1])*np.nan
        else:
            if X == '0':
                reg2 = re.compile(r'^(.{3})',re.M)
            elif X == '2':
                reg2 = re.compile(r'^.{54}(.{3})',re.M)
            ms = reg2.finditer(v)
            d = np.arange(0,dtype=np.float32)
            for i in ms:
                x = i.group(1)
                d = np.hstack((d,intORnan(x)))
    return d

''' 测试所有数据
stationNo = [54428,54525,54523,54529,54619,54527,54528,54517,54526,54622,54645,54530,54623,99999]
for i in stationNo[:-1]:
    for y in range(1951,2014):
        for m in ['01','02','03','04','05','06','07','08','09','10','11','12']:
            f = os.path.join(r"D:\mytornado\Afiles",str(i),'A'+str(i)+'-'+str(y)+m+'.TXT')
            try:
                open(f)
            except IOError:
                print('')
            else:
                print(f)
                d = R(f);print('R');print(d)
                d = T(f);print('T');print(d)
                d = Tx(f);print('Tx');print(d)
                d = Tn(f);print('Tn');print(d)
                d = F(f);print('F');print(d)
                d = Fx(f);print('Fx');print(d)
                d = S(f);print('S');print(d)
                d = RH(f);print('RH');print(d)
                d = RHn(f);print('RHn');print(d)
#'''
