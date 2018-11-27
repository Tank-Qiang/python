#!/usr/bin/env python
#coding:utf-8
#by-wenqiang
#!/usr/bin/env python
# -*- coding: UTF8 -*-

import linecache
import sys
import requests
import os
import commands
import time
log_dir = '/data/log/apps/red/'
test_url = "http://hostname/alarm/receptor"
old_txt = '/data/log/apps/'
sys_time1 = time.strftime('%Y-%m-%d',time.localtime(time.time()))
log_name1 = "red-"+sys_time1
project = 'test'
#需要注意的是：首次执行脚本前需要执行两次
#对比当前切割文件是否是整点文件，如果是整点文件则继续读旧文件
#脚本生成了一个sys_file.old 用于记录每次打开的文件时间戳
def diff_file():
    os.environ['old_txt']=str(old_txt)
    old_ex = commands.getstatusoutput('ls $old_txt')
    if int (old_ex[0]) == 0:
        if os.path.getsize(old_txt) > 1:
            oldf = open(old_txt,'r')
            oldread = int(oldf.read())
            now_sys = int(sys_time1)
            oldf.close()
       #此处判断为整点文件切割判断，如果当前时间戳和文件名一致则继续，否则读旧文件读完重写旧文件
            if oldread == now_sys:
                #print 'not change'
                log_file_check(log_name1)

            else:
               oldf1 = open(old_txt,'r+')
               log_oldname = oldf1.read()
               log_old_name = log_oldname.strip('\n')
               log_old = "red-"+log_old_name
               oldf1.close()
               print log_old_name
               print log_old
               oldf4 = open(old_txt,'w+')
               oldf4.write(sys_time1)
               oldf4.close()
               log_file_check(log_old)
        else:
             oldf2 = open(old_txt,'w+')
             oldf2.write(sys_time1)
             oldf2.close()
             diff_file()
    else:
        with open(old_txt,'w+') as oldf3:
            oldf3.write(sys_time1)
            print 'not sys file'
            diff_file()

#这里用于接受diff_file传过来的函数，上面判断中可以传不同的文件名到此函数
#并判断该日志文件是否存在
def log_file_check(cmd_name):
    log_path = log_dir+cmd_name
    os.environ['log_path']=str(log_path)
    log_ex = commands.getstatusoutput('ls $log_path')
    if int(log_ex[0]) == 0:
       error_check(log_path)
    else:
       print log_path
       print '日志不存在'
       sys.exit()
#这里生成并检查上次读取文件的行号，如果行号一致则说明日志没有增加则不读取，exit
def error_check(path):
    filename = path
    count = len(open(filename,'rU').readlines())
    num_file = '/data/log/apps/no_move.txt'
    os.environ['num_file']=str(num_file)
    log_ex = commands.getstatusoutput('ls $num_file')
    if int(log_ex[0]) == 0:
        if  os.path.getsize(num_file) > 0:
            f = open(num_file,'r')
            num_read = f.read()
            num_read = int(num_read)
            f.close()
            if num_read == count:
                print 'log is not change'
                sys.exit()
            else:
                f = open(num_file,'w+')
                f.write(str(count))
                f.close()
                grep_key(num_read,filename)
        else:
            f = open(num_file,'w+')
            f.write(str(count))
            f.close()
            error_check(path)
    else:
        f = open(num_file,'w+')
        f.close()
        error_check(path)
#这里是接收传过来的更新行号，从最新行号读取后面的日志过滤我们的关键字发送报警
def grep_key(num,logname):
    num_now = num
    name_now = logname
    vl = 'netease api request http code'
    with open(name_now,'r') as file:
        key_list = file.readlines()[num_now:]
        for line in key_list:
            if vl in line:
               name = project%"业务日志error"
               product = "test_RED"
               content = line
               html_content = line
               send_test(name, product, content, html_content)
            else:
                pass
def send_test(name, product, content, html_content):
    payload = {
            "name": name,
            "group": 2,
            "product": product,
            "priority": 2,
            "content": content,
            "html_content": html_content,
            "no_deal": 0
        }
    r = requests.post(test_url, data=payload)
    print r.status_code


if __name__ == "__main__":
    diff_file()