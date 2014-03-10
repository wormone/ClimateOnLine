# -*- coding: utf8 -*-
import os
import numpy as np
from myfunctions import station,stationNo,DATAPATH,days36x
from variables import R

''' 要素 '''
precipitation = ['累计降水量','日降水量大于等于0.1mm日数','日降水量大于等于1mm日数',\
                 '小雨日数','中雨日数','大雨日数','暴雨日数']

# 定义函数 R_addtod，调用方式如下：
# d = R_addtod(filename,d)
def R_addtod(filename,d):
    try:
        x = R(filename)
    except (IOError,TypeError,NameError):
        d = ''
    else:
        d = np.hstack((d,x))
    return d


''' 定义降水的计算函数 myreadaR
    参数 above：表示日降水量大于等于 above
         below：表示日降水小于等于 below
         daysorsum："days" 表示计算日数，"sum" 表示计算累计降水量
    如统计累计降水量：
    year,s = myreadaR('54525',1951,2013,1,12,1,31,0,99999,"sum") # 这里用 99999 表示不可能的大数
    返回的 s 单位是 mm 或 d
'''
def myreadaR(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,above,below,daysorsum):
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
                d = R_addtod(filename,d)
                if d == '': break
        else:
            ''' 起始月日晚于终止月日，跨年 '''
            ''' 第一年 '''
            monthA = np.arange(startmonth,13)
            for j in monthA:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                d = R_addtod(filename,d)
                if d == '': break
            ''' 第二年 '''
            if d != '':
                # 第一年数据缺月，不再检索第二年的月
                monthB = np.arange(1,endmonth+1)
                for j in monthB:
                    filename = 'A'+stationnumber+'-'+str((years[i]+1)*100+j)+'.TXT'
                    d = R_addtod(filename,d)
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
                if daysorsum == 'sum':
                    s[i] = np.nansum((d>above*10)*(d<below*10)*d)
                elif daysorsum == 'days':
                    s[i] = np.sum((d>above*10)*(d<below*10))
    if daysorsum == 'sum':
        # 单位由 0.1mm 转换为 mm
        s = np.rint(s)*0.1
    return years,s


''' 定义计算全市平均的函数 myreadaRM，调用方式比 myreadaR 少了参数 stationnumber
    返回 years 为年份序列，s 为全市平均序列，z 为各站序列
'''
def myreadaRM(startyear,endyear,startmonth,endmonth,startday,endday,above,below,daysorsum):
    z = np.zeros([len(station)-1,endyear-startyear+1])
    n = np.arange(len(station)-1)
    for i in n:
        stationnumber = str(stationNo[i])
        years,data = myreadaR(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,above,below,daysorsum)
        z[i] = data
    s = np.nanmean(z, axis=0)
    # 注意保留一位小数
    s = np.rint(s*10)*0.1
    return years,z,s
