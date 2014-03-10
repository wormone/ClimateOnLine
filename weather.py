# -*- coding: utf-8 -*-
import re
import os
import numpy as np
from myfunctions import station,stationNo,DATAPATH,days36x

''' 要素 '''
weather = {"霾":'05',"雾":'42',"轻雾":'10',"雨":'60',"雪":'70',\
           "露":'01',"霜":'02',"结冰":'03',"烟幕":'04',"浮尘":'06',\
           "扬沙":'07',"尘卷风":'08',"闪电":'13',"大风":'15',"积雪":'16',\
           "极光":'14',"雷暴":'17',"飑":'18',"龙卷":'19',"沙尘暴":'31',\
           "吹雪":'38',"雪暴":'39',"雾凇":'48',"毛毛雨":'50',"雨凇":'56',\
           "雨夹雪":'68',"冰针":'76',"米雪":'77',"冰粒":'79',"阵雨":'80',\
           "阵性雨夹雪":'83',"阵雪":'85',"霰":'87',"冰雹":'89'}

# 定义函数 W0_addtovalues()，调用方式如下：
# values = W0_addtovalues(filename,values,weathercode)
def W0_addtovalues(filename,values,weathercode):
    try:
        value,v = myreadaW0(filename,weathercode)
    except IOError:
        #print('There is no ' + filename)
        values = ''
    except (TypeError,NameError):
        # 市区 54517 站自 2013 年 1 月开始没有 W0 段记录了……
        values = ''
    else:
        #print('Processing ' + str(years[i]*100+j))
        values = values + value
    return values

''' 定义读取 A 文件天气现象记录的函数 myreadaW0，函数调用方式如下
    filename = r"A54428-201305.TXT"
    weathercode = weather.get("霾")
    value,v = myreadaW0(filename,weathercode)
    返回字符串 value 用 1,0 表示出现与否，数组 v 为整形 1,0 序列
'''
def myreadaW0(filename,weathercode):
    # 用 read() 将读取整个文件为一个字符串记录（含换行 \n）
    file = open(filename)
    '''
    # 注意要打开的文件的编码，python3 需要指定出来，否则会出错
    file = open(filename, encoding="ISO-8859-1")
    # iso-8859-1 或 latin-1 表示 ANSI 编码
    '''
    str = file.read()
    file.close()
    ''' 删除 \r 符号，不管有没有，都删除 '''
    str = re.sub(r'\r','',str)
    # 匹配天气现象段的记录：以 W0 以下至第一个以 = 结束的所有行
    # re.M 表示多行模式，re.S 表示 . 匹配任何符号包括换行符 \n
    ''' 【特别注意】 Windows 和 linux 下文本文件的换行符号分别是 \r\n 和 \n
        python2 使用 open() 和 read() 读取的文件内容，如果文件是 windows 下的，
        那就要特别注意这个问题。re.M 时，$ 会匹配掉 \r，如果做替换需注意。
    '''
    reg = re.compile(r"^W0\n(.+?(?==))",re.M+re.S)
    # finditer() 返回一个顺序访问每一个匹配结果的迭代器
    # 其实这里只有一个匹配结果
    matchs = reg.finditer(str)
    # 关闭文件 file
    file.close()
    # 用 for ... in ... 访问每一个匹配结果
    for match in matchs:
        # 由于 reg 只有一个匹配模式，因此匹配结果就是 group(1)
        value = match.group(1)
        # 将非 . 符号后的换行符删除，合并为一行，是一天的记录
        value = re.sub(r'(?<=[^.])\n',',',value)
        #print('天气现象记录段：')
        #print(value)
        # 匹配所有含有单词 '05' 的行，注意 '05' 前后都是非数字字符！
        p = re.compile(r'^.*(?<!\d)'+weathercode+'(?!\d).*$',re.M)
        value = p.sub('1', value)
        # 匹配所有非 1 的行
    	# 或者匹配所有含有 . 符号的行
        p = re.compile(r'^.*\..*$',re.M)
        value = p.sub('0', value)
        # value 为一个字符串记录：
        # 1 表示出现天气现象，0 表示未出现
        value = re.sub(r'\n','',value)
        v = np.arange(len(value))
        for i in v:
            v[i] = int(value[i])
        return value,v
        # 返回数组 v，1 表示出现天气现象，0 表示未出现

''' 定义计算任意时段【历史同期】某种天气现象出现次数的函数 myreadaW0para，调用方式如下
    stationnumber = station.get("蓟县")
    startyear = int('1961')
    endyear = int('2013')
    startmonth = int('1')
    endmonth = int('12')
    startday = int('1')
    endday = int('31')
    weathercode = weather.get("霾")
    years,s = myreadaW0para(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,weathercode)
    返回数组 s 为年序列，某时段历史同期累计值，任何月份数据缺失都将导致 nan
    返回数组 years 为年份序列
    注：当起始月日晚于终止月日时，该函数做跨年处理
'''
def myreadaW0para(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,weathercode):
    P = os.path.join(DATAPATH,stationnumber)
    os.chdir(P)
    years = np.arange(startyear,endyear+1)
    # 年处理，用 s 记录每年求和的数值
    s = np.arange(len(years),dtype=np.float32)
    # 特别要注意指明 s 的数据类型为 np.float32，因为 np.nan 的数据类型如此，后面要用到
    for i in s:
        i = int(i)
        # 判断是否闰年
        daysfit = days36x(years[i])
        ''' 逐月处理，对空字符串 values 开始追加 '''
        values = ''
        # 用 values 记录每年起始日期到终止日期的 0,1 字符序列
        if startmonth*100+startday <= endmonth*100+endday:
            ''' 起始月日早于或等于终止月日，不跨年 '''
            months = np.arange(startmonth,endmonth+1)
            for j in months:
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                values = W0_addtovalues(filename,values,weathercode)
                if values == '': break
        else:
            ''' 起始月日晚于终止月日，跨年 '''
            ''' 第一年 '''
            monthA = np.arange(startmonth,13)
            for j in monthA:
                # 年份是 years[i]
                filename = 'A'+stationnumber+'-'+str(years[i]*100+j)+'.TXT'
                values = W0_addtovalues(filename,values,weathercode)
                if values == '': break
            ''' 第二年 '''
            if values != '':
                # 第一年数据缺月，不再检索第二年的月
                monthB = np.arange(1,endmonth+1)
                for j in monthB:
                    # 年份是 years[i]+1
                    filename = 'A'+stationnumber+'-'+str((years[i]+1)*100+j)+'.TXT'
                    values = W0_addtovalues(filename,values,weathercode)
                    if values == '': break
        ''' 月处理完毕，得到字符串 values，开始年处理 '''
        if values == '':
            # 如果有任意一个月份数据缺失，则以 nan 表示该年缺失
            s[i] = np.nan
        else:
            # 如果数据齐全，则开始以下处理
            # 删除起始日之前
            values = values[startday-1:]
            # 删除终止月之后：a dirty trick
            if daysfit[j-1]-endday > 0:
            # 如果截止日期是闰年2月29日，daysfit[j-1]-endday 在非闰年为 -1，保持 values 不变
                values = values[::-1]
                values = values[daysfit[j-1]-endday:] # 注意这里的索引 [j-1]
                values = values[::-1]
            # 将字符串 values 转换为数组 d，该方法已固定如下
            d = np.arange(len(values))
            for k in d:
                d[k] = int(values[k])
            # 求和计入数组 s
            s[i] = np.sum(d)
    return years,s


''' 定义计算全市平均的函数 myreadaW0paraM，调用方式比 myreadaW0para 少了参数 stationnumber
    返回 years 为年份序列，s 为全市平均序列，z 为各站序列
'''
def myreadaW0paraM(startyear,endyear,startmonth,endmonth,startday,endday,weathercode):
    z = np.zeros([len(station)-1,endyear-startyear+1])
    # 先构造一个行数为 len(station)-1，列数为 endyear-startyear+1 的零多维数组 z，预存各站序列
    # len(station)-1 是因为 station 包括了"全市平均"
    n = np.arange(len(station)-1)
    # stationNo = [54428,54525,54523,54529,54619,54527,54528,54517,54526,54622,54645,54530,54623,99999]
	# stationNo 最后的 99999 表示全市平均
    for i in n:
        stationnumber = str(stationNo[i])
        years,data = myreadaW0para(stationnumber,startyear,endyear,startmonth,endmonth,startday,endday,weathercode)
        z[i] = data
    s = np.nanmean(z, axis=0)
    s = np.rint(s*10)*0.1
    return years,z,s
