# -*- coding: utf8 -*-
import os
import numpy as np
from myfunctions import station,stationNo,DATAPATH,days36x
from variables import RH,RHn

''' 要素 '''
humidity = ['平均相对湿度','平均最小相对湿度','最小相对湿度最小值']

# 定义函数 H_addtod，调用方式如下：
# d = H_addtod(filename,d,MMM)
def H_addtod(filename,d,MMM):
    try:
        if MMM == 'mean':
            x = RH(filename)
        elif MMM == 'meanmin' or MMM == 'minmin':
            x = RHn(filename)
    except (IOError,TypeError,NameError):
        d = ''
    else:
        d = np.hstack((d,x))
    return d


''' 定义相对湿度的计算函数 myreadaRH
    参数 MMM："mean" 表示平均相对湿度，"meanmin" 表示平均最小相对湿度，"minmin" 表示最小相对湿度最小值
    如计算平均相对湿度，调用方式如下：
    year,s = myreadaRH('54525',1951,2013,1,12,1,31,"mean")
    返回的 s 单位是 %
'''
def myreadaRH(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,MMM):
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
                d = H_addtod(filename,d,MMM)
                if d == '': break
        else:
            ''' 起始月日晚于终止月日，跨年 '''
            ''' 第一年 '''
            monthA = np.arange(startmonth,13)
            for j in monthA:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                d = H_addtod(filename,d,MMM)
                if d == '': break
            ''' 第二年 '''
            if d != '':
                # 第一年数据缺月，不再检索第二年的月
                monthB = np.arange(1,endmonth+1)
                for j in monthB:
                    filename = 'A'+stationnumber+'-'+str((years[i]+1)*100+j)+'.TXT'
                    d = H_addtod(filename,d,MMM)
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
                if MMM == 'mean' or MMM == 'meanmin':
                    s[i] = np.rint(np.nanmean(d)) # 保留整数
                elif MMM == 'minmin':
                    s[i] = np.nanmin(d)
    return years,s


''' 定义计算全市平均的函数 myreadaRHM，调用方式比 myreadaRH 少了参数 stationnumber
    返回 years 为年份序列，s 为全市平均序列，z 为各站序列
'''
def myreadaRHM(startyear,endyear,startmonth,endmonth,startday,endday,MMM):
    z = np.zeros([len(station)-1,endyear-startyear+1])
    n = np.arange(len(station)-1)
    for i in n:
        stationnumber = str(stationNo[i])
        years,data = myreadaRH(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,MMM)
        z[i] = data
    s = np.nanmean(z, axis=0)
    # 保留整数
    s = np.rint(s)
    return years,z,s
