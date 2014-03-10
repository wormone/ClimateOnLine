# -*- coding: utf8 -*-
import os
import numpy as np
from myfunctions import station,stationNo,DATAPATH,days36x
from variables import S

''' 要素 '''
sunshine = ['平均日照时数','累计日照时数']

# 定义函数 S_addtod，调用方式如下：
# d = S_addtod(filename,d)
def S_addtod(filename,d):
    try:
        x = S(filename)
    except (IOError,TypeError,NameError):
        d = ''
    else:
        d = np.hstack((d,x))
    return d

''' 定义相对湿度的计算函数 myreadaS
    参数 MMM："mean" 表示平均，"sum" 表示累计
    如计算累计日照时数，调用方式如下：
    year,s = myreadaF('54525',1951,2013,1,12,1,31,"sum")
    返回的 s 单位是米每秒
'''
def myreadaS(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,MMM):
    P = os.path.join(DATAPATH,stationnumber)
    os.chdir(P)
    years = np.arange(startyear,endyear+1)
    s = np.arange(len(years),dtype=np.float32)
    for i in s:
        i = int(i)
        daysfit = days36x(years[i])
        ''' 逐月处理，对空字数组 d 开始追加 '''
        d = np.arange(0,dtype=np.float32)
        if startmonth*100+startday <= endmonth*100+endday:
            ''' 起始月日早于或等于终止月日，不跨年 '''
            months = np.arange(startmonth,endmonth+1)
            for j in months:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                d = S_addtod(filename,d)
                if d == '': break
        else:
            ''' 起始月日晚于终止月日，跨年 '''
            ''' 第一年 '''
            monthA = np.arange(startmonth,13)
            for j in monthA:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                d = S_addtod(filename,d)
                if d == '': break
            ''' 第二年 '''
            if d != '':
                # 第一年数据缺月，不再检索第二年的月
                monthB = np.arange(1,endmonth+1)
                for j in monthB:
                    filename = 'A'+stationnumber+'-'+str((years[i]+1)*100+j)+'.TXT'
                    d = S_addtod(filename,d)
                    if d == '': break
        ''' 月处理完毕，开始年处理 '''
        if d == '':
            s[i] = np.nan
        else:
            d = d[startday-1:]
            if daysfit[j-1]-endday > 0:
                d = d[::-1]
                d = d[daysfit[j-1]-endday:]
                d = d[::-1]
            if np.sum(np.isnan(d))*4 >= len(d):
                # 如果日值缺测率大于等于 1/4
                s[i] = np.nan
            else:
                if MMM == 'mean':
                    s[i] = np.nanmean(d)
                elif MMM == 'sum':
                    s[i] = np.nansum(d)
    # 单位由 0.1 h 转换为 h
    s = np.rint(s)*0.1
    return years,s


''' 定义计算全市平均的函数 myreadaSM，调用方式比 myreadaS 少了参数 stationnumber
    返回 years 为年份序列，s 为全市平均序列，z 为各站序列
'''
def myreadaSM(startyear,endyear,startmonth,endmonth,startday,endday,MMM):
    z = np.zeros([len(station)-1,endyear-startyear+1])
    n = np.arange(len(station)-1)
    for i in n:
        stationnumber = str(stationNo[i])
        years,data = myreadaS(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,MMM)
        z[i] = data
    s = np.nanmean(z, axis=0)
    # 注意保留一位小数
    s = np.rint(s*10)*0.1
    return years,z,s
