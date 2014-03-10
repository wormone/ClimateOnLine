#! /bin/sh -
# 【问题概述】修改 A0 文件的文件名，使其与 A 文件的命名规则一致。
# 【具体分析】A0 文件名形如 A054428.J99，其中 54428 为区站号，
#             J 表示 1 月份，99 表示 1999 年。
#             JFMAYULGSOND 分别表示 1 至 12 月。
#             05 年有 A0 文件与 A 文件并存的情况，需注意。
#             A 文件名形如 A54428-201305.TXT。
#【流程分解】
# 设置区站号，或可采用 read n
read n
cd ${n}
# 备份 2005 年的 A0 文件到新建路径下
mkdir ./05bak
mv A0${n}.*05 ./05bak/
# 查找所有 A0 文件的文件名并寄存到变量 a
# 这里重点要注意 find 命令使用正则表达式的方式
a=$(find . -regextype posix-extended -regex "./A0${n}.[[:upper:]][[:digit:]]{2}")
# 对每个文件名进行处理
# 这里注意 for 循环针对变量 $a 的操作方式
for i in $a
do
  # 这里注意，先将文件名寄存到变量 I，这是个好习惯
  I=$i
  # 提取 A0 文件名中表示月份的字母
  month=${I:10:1}
  # 字母与月份的转换关系
  case $month in 
  J) MM=01;;
  F) MM=02;;
  M) MM=03;;
  A) MM=04;;
  Y) MM=05;;
  U) MM=06;;
  L) MM=07;;
  G) MM=08;;
  S) MM=09;;
  O) MM=10;;
  N) MM=11;;
  D) MM=12;;
  esac
  # 提取 A0 文件名中表示年份的两个数字字符
  year=${I:11:2}
  # 区别 20?? 年与 19?? 年
  y=${year:0:1}
  if [ "X$y" = "X0" ]
  then YYYY=20${year}
  else YYYY=19${year}
  fi
  # 用复制的方式改变文件名，保留原 A0 文件
  cp $i A${n}-${YYYY}${MM}.TXT
done
# 复原 2005 年的 A0 文件
mv ./05bak/* .
rm -Rf ./05bak
# EOF
