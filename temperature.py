# -*- coding: utf8 -*-
import os
import numpy as np
from myfunctions import station,stationNo,DATAPATH,days36x
from variables import T,Tx,Tn

''' 要素 '''
temperature = ['平均气温','平均最高气温','平均最低气温','极端最高气温','极端最低气温',\
               '0度以上活动积温','10度以上活动积温','0度以下负积温',\
               '35度以上高温日数','-10度以下低温日数']

# 定义函数 T_addtod，调用方式如下：
# d = T_addtod(filename,d,tmtxtn)
def T_addtod(filename,d,tmtxtn):
    try:
        if tmtxtn == 'tm':
            x = T(filename)
        elif tmtxtn == 'tx':
            x = Tx(filename)
        elif tmtxtn == 'tn':
            x = Tn(filename)
    except (IOError,TypeError,NameError):
        d = ''
    else:
        d = np.hstack((d,x))
    return d
			   
			   
''' 定义气温的计算函数 myreadaT
    参数 tmtxtn：'tm' 表示平均气温，'tx' 表示最高气温，'tn' 表示最低气温
            MMM: 'mean' 表示求平均，'max' 表示取最大值，'min' 表示取最小值
    如统计极端最高气温：
    year,s = myreadaT('54525',1951,2013,1,12,1,31,'tx','max')
    返回的 s 单位是摄氏度
'''
def myreadaT(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,MMM):
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
                d = T_addtod(filename,d,tmtxtn)
                if d == '': break
        else:
            ''' 起始月日晚于终止月日，跨年 '''
            ''' 第一年 '''
            monthA = np.arange(startmonth,13)
            for j in monthA:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                d = T_addtod(filename,d,tmtxtn)
                if d == '': break
            ''' 第二年 '''
            if d != '':
                # 第一年数据缺月，不再检索第二年的月
                monthB = np.arange(1,endmonth+1)
                for j in monthB:
                    filename = 'A'+stationnumber+'-'+str((years[i]+1)*100+j)+'.TXT'
                    d = T_addtod(filename,d,tmtxtn)
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
                    s[i] = np.rint(np.nanmean(d))
                elif MMM == 'max':
                    s[i] = np.nanmax(d)
                elif MMM == 'min':
                    s[i] = np.nanmin(d)
    # 先取整数再乘以 0.1，即保留一位小数
    s = np.rint(s)*0.1
    return years,s


''' 定义计算积温的函数 myreadaTsum
    参数 threshold：阈值，如 0、5、10 等
            method: 方法，'gt' 表示大于等于，'lt' 表示小于等于
    如计算负积温：
    year,s = myreadaTsum('54525',1951,2013,1,12,1,31,0,'lt')
    返回的 s 单位是摄氏度
'''
def myreadaTsum(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,threshold,method):
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
                d = T_addtod(filename,d,'tm')
                if d == '': break
        else:
            ''' 起始月日晚于终止月日，跨年 '''
            ''' 第一年 '''
            monthA = np.arange(startmonth,13)
            for j in monthA:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                d = T_addtod(filename,d,'tm')
                if d == '': break
            ''' 第二年 '''
            if d != '':
                # 第一年数据缺月，不再检索第二年的月
                monthB = np.arange(1,endmonth+1)
                for j in monthB:
                    filename = 'A'+stationnumber+'-'+str((years[i]+1)*100+j)+'.TXT'
                    d = T_addtod(filename,d,'tm')
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
                # 处理 method 和 threshold，注意 threshold 乘以 10 数量级才对
                if method == 'gt':
                    q = d>=threshold*10
                elif method == 'lt':
                    q = d<=threshold*10
                s[i] = np.nansum(d*q)
    # 先取整数再乘以 0.1，即保留一位小数
    s = np.rint(s)*0.1
    return years,s

''' 定义计算气温日数的函数 myreadaTdays
    参数 tmtxtn：'tm' 表示平均气温，'tx' 表示最高气温，'tn' 表示最低气温
      threshold：阈值，如 0、5、10 等
         method: 方法，'gt' 表示大于等于，'lt' 表示小于等于
    如统计大于等于35度的高温日数：
    year,s = myreadaTdays('54525',1951,2013,1,12,1,31,'tx',35,'gt')
    返回的 s 单位是日数
'''
def myreadaTdays(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,threshold,method):
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
                d = T_addtod(filename,d,tmtxtn)
                if d == '': break
        else:
            ''' 起始月日晚于终止月日，跨年 '''
            ''' 第一年 '''
            monthA = np.arange(startmonth,13)
            for j in monthA:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                d = T_addtod(filename,d,tmtxtn)
                if d == '': break
            ''' 第二年 '''
            if d != '':
                # 第一年数据缺月，不再检索第二年的月
                monthB = np.arange(1,endmonth+1)
                for j in monthB:
                    filename = 'A'+stationnumber+'-'+str((years[i]+1)*100+j)+'.TXT'
                    d = T_addtod(filename,d,tmtxtn)
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
                # 处理 method 和 threshold，注意 threshold 乘以 10 数量级才对
                if method == 'gt':
                    q = d>=threshold*10
                elif method == 'lt':
                    q = d<=threshold*10
                s[i] = np.nansum(q)
    return years,s

''' 调用上述函数查看结果
year,s = myreadaT('54525',1951,2013,1,12,1,31,'tx','max')
print year;print s
year,s = myreadaTsum('54517',1951,2013,12,2,1,28,0,'lt')
print year;print s
year,s = myreadaTdays('54525',1951,2013,1,12,1,31,'tx',35,'gt')
print year;print s
'''

''' 定义计算全市平均的函数 myreadaTM，调用方式比 myreadaT 少了参数 stationnumber
    返回 years 为年份序列，s 为全市平均序列，z 为各站序列
'''
def myreadaTM(startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,MMM):
    z = np.zeros([len(station)-1,endyear-startyear+1])
    n = np.arange(len(station)-1)
    for i in n:
        stationnumber = str(stationNo[i])
        years,data = myreadaT(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,MMM)
        z[i] = data
    s = np.nanmean(z, axis=0)
    # 注意保留一位小数
    s = np.rint(s*10)*0.1
    return years,z,s

''' 定义计算全市平均的函数 myreadaTsumM，调用方式比 myreadaTsum 少了参数 stationnumber
    返回 years 为年份序列，s 为全市平均序列，z 为各站序列
'''
def myreadaTsumM(startyear,endyear,startmonth,endmonth,startday,endday,threshold,method):
    z = np.zeros([len(station)-1,endyear-startyear+1])
    n = np.arange(len(station)-1)
    for i in n:
        stationnumber = str(stationNo[i])
        years,data = myreadaTsum(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,threshold,method)
        z[i] = data
    s = np.nanmean(z, axis=0)
    # 注意保留一位小数
    s = np.rint(s*10)*0.1
    return years,z,s
	
''' 定义计算全市平均的函数 myreadaTdaysM，调用方式比 myreadaTdays 少了参数 stationnumber
    返回 years 为年份序列，s 为全市平均序列，z 为各站序列
'''
def myreadaTdaysM(startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,threshold,method):
    z = np.zeros([len(station)-1,endyear-startyear+1])
    n = np.arange(len(station)-1)
    for i in n:
        stationnumber = str(stationNo[i])
        years,data = myreadaTdays(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,tmtxtn,threshold,method)
        z[i] = data
    s = np.nanmean(z, axis=0)
    # 注意保留一位小数
    s = np.rint(s*10)*0.1
    return years,z,s

''' 调用上述函数的示例
year,z,s = myreadaTdaysM(1951,2013,1,12,1,31,'tx',35,'gt')
print year;print z;print s
#'''
