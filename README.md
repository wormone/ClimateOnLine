ClimateOnLine
=============

一个提供气候数据（A0/A 文件）分析与绘图服务的 WebApp

## 简介

* 一个简单的 WebApp，基于 python Tornado 框架
* Tornado 本就是一个轻量级的 Web 框架，这个应用更是轻量级中的轻量级
* 核心是文本数据的处理、计算、读写、绘图，采用的关键模块包括 re、numpy、matplotlib 等
* 还包括了一个自编的超轻量级的用户管理功能，采用了 redis 数据库

## 源文件简要说明

* /static/ 静态文件
* /templates/ 网页模板文件
* /myrenameA0toA.sh 将 A0 文件名转换为 A 文件名的脚本
* /myfunctions.py 基础信息和常用函数
* /variables.py 读取 A0/A 文件各要素的函数
* /temperature.py 处理气温序列的函数
* /precipitation.py 处理降水序列的函数
* /humidity.py 处理相对湿度序列的函数
* /windspeed.py 处理风速序列的函数
* /sunshine.py 处理日照序列的函数
* /weather.py 处理天气现象序列的函数
* /climatewebsiteNEW.py 主程序

## 便捷的可扩展性

1. 数据地域范围：省（市）级、区域级、国家级，可自由、简单配置
2. 数据时间范围：外部程序将当月数据写成 A 文件格式，即可实现历史数据和实时数据的无缝化连接
3. 增加要素：可参照已有参数的处理办法，快速增加新的要素
4. 新的分析和绘图功能：TODO
