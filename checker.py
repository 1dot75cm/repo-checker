#!/usr/bin/env python2
#coding=utf-8
'''
@author: mosquito
@email: sensor.wen@gmail.com
@project: Checker
@github: http://github.com/1dot75cm/repo-checker
@description: Checker is used to check update for software.
@version: 0.1
@history:
    0.1 - Initial version (2016.01.05)
'''

from __future__ import print_function
import urllib
import re
import time
import csv
import json
import sys
import os

def load_data(file):
    ''' Load csv file.

    CSV Format:
      "1,1,lwqq,https://github.com/xiehuc/lwqq,master,733836e,150202"

    Sub Package: 0. normal 1. subpkg
    Url Type: 1. github 2. google 3. bitbucket 4. sogou 5. tragtor 6. youdao
      7. opera 8. pacman 9. apt 10. nginx 11. ccal 12. sandbox 14. wps
      20. qt-installer-freamwork 21. pycharm
    Name, Url, Branch, RPM Commit, RPM Update Time, Others

    return list '''

    csvlist = list()
    with open(file, 'rb') as csvfile:
        content = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in content:
            csvlist.append(row)
    return csvlist

def get_page(url, url_type):
    ''' 获取整个页面数据
    return str '''

    if url_type == "2":
        return "None Content"
    elif url_type == "4":
        return urllib.urlopen(url).read().decode('gb2312').encode('utf-8')
    else:
        return urllib.urlopen(url).read()

def get_date(page, url_type):
    ''' 获取 date -> 150708
    return str '''

    time_format = "%Y-%m-%d"
    pattern = r'.*datetime="(.*)T'

#    if url_type in ["1", "3"]:
#        pattern = r'.*datetime="(.*)T'
    if url_type in ["4", "6", "14"]:
        pattern = r'([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})'
    elif url_type == "5":
        page = page.split("tragtor")[4]
        pattern = r'time.>(.*[0-9]{4})'
        time_format = "%a %b %d %H:%M:%S %Y"
    elif url_type == "7":
        if page.splitlines()[-3].find("info") > -1:
            page = page.splitlines()[-4]
        else:
            page = page.splitlines()[-3]
        pattern = r'([0-9]{2}-.{3}-[0-9]{4})'
        time_format = "%d-%b-%Y"
    elif url_type == "8":
        pattern = r'tag.*([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})'
    elif url_type == "9":
        pattern = r'id=\w{40}.*([0-9]{4}-[0-9]{2}-[0-9]{2})'
    elif url_type == "10":
        pattern = r'([0-9]{2}\s.{3}\s[0-9]{4})'
        time_format = "%d %b %Y"
    elif url_type == "11":
        pattern = r'([A-Z].*\s[0-9]{1,2},\s[0-9]{4})'
        time_format = "%B %d, %Y"
    elif url_type == "12":
        pattern = r'id=\w{40}.*tag-deco.*([0-9]{4}-[0-9]{2}-[0-9]{2})'
    elif url_type == "20":
        pattern = r'([0-9]{2}-.{3}-[0-9]{4})'
        time_format = "%d-%b-%Y"
    elif url_type == "21":
        page = json.loads(page)['PCC'][0]['date']
        pattern = r'(.*)'

    try:
        d = re.search(pattern, page, re.M).group(1)
        t = time.strptime(d, time_format)
        short_time = time.strftime("%y%m%d", t)
    except AttributeError, TypeError:
        short_time = "None"

    return short_time

def get_commit(page, url_type):
    ''' 获取 commit
    return str '''

    pattern = r'.*commit/([a-z0-9]*)\"'

    if url_type == "9":
        pattern = r'id=(\w{40})'
    elif url_type == "12":
        pattern = r'id=(\w{40}).*tag-deco'

    try:
        c = re.search(pattern, page, re.M).group(1)
    except AttributeError, TypeError:
        c = "None"

    return c

def get_info(*item):
    ''' 获取页面commit和date
    return datalist'''

    item = item[0]
    if len(item) == 0 or item[0][0] == "#":
        return None

    sub_pkg, url_type, name, url = item[0], item[1], item[2], item[3]
    branch, rpm_com, rpm_date = item[4], item[5], item[6]

    type_num = ["3", "4", "5", "6", "7", "9", "10", "11", "12", "14", "20", "21"]

    if url_type in type_num:
        release_url, latest_url = url.replace('%2',','), url.replace('%2',',')
    else:
        release_url = url + "/releases"
        latest_url = url + "/commits/" + branch

    page = get_page(release_url, url_type)
    release_date = get_date(page, url_type)
    release_com = get_commit(page, url_type)

    page = get_page(latest_url, url_type)
    latest_date = get_date(page, url_type)
    latest_com = get_commit(page, url_type)

    if rpm_date == latest_date or rpm_date >= release_date:
        status = "normal"
    else:
        status = "update" + "[" + url + "]"

    itemlist = [sub_pkg, name, rpm_date, rpm_com, release_date, release_com, latest_date, latest_com, status]

    return output(0, *itemlist)

def output(title=0, *datalist):
    ''' Output.
    Sub Package: 0. normal 1. subpkg '''

    if title == 1:
        print("# Generation date:", localtime(1), \
              "\n Name".ljust(23) + \
              "RPM-Version".ljust(16) + \
              "Rel-Version".ljust(16) + \
              "Latest-Commit".ljust(16) + \
              "Status")
    else:
        if datalist[0] == "1":
            name = "- " + datalist[1]
        else:
            name = datalist[1]

        rpm_ver = datalist[2] + "[" + datalist[3][:7] + "]"
        rel_ver = datalist[4] + "[" + datalist[5][:7] + "]"
        lat_ver = datalist[6] + "[" + datalist[7][:7] + "]"
        print(str(name).ljust(22) + \
              str(rpm_ver).ljust(16) + \
              str(rel_ver).ljust(16) + \
              str(lat_ver).ljust(16) + \
              str(datalist[8]))

def localtime(trigger=1):
    ''' return current localtime and seconds. '''

    global start_sec, stop_sec
    if trigger == 1:
        start_sec = time.time()
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    elif trigger == 0:
        stop_sec = time.time()
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), stop_sec - start_sec

def helper(**opts):
    ''' display help information. '''

    doclist = list()
    for i in __doc__.splitlines():
        if i.startswith("@") and i.find(": ") > -1:
            doclist.append(i.split(': ')[1])
    author, email, project, github, description, version = doclist

    if opts['help'] == 1 and opts['err'] == 0:
        print('''{}
Usage: {_name} [OPTION]...

Options:
  -m, --mode=MODE  {_name} work mode: 0 single, 1 thread(default)
  -f, --file=PATH  {_name} data(csv) full path
  -h, --help       display this help and exit
  -v, --version    output version information and exit'''.format(
            description,
            _name=project.lower())
        )
        sys.exit()

    elif opts['vers'] == 1 and opts['err'] == 0:
        print('''{} version {}
Written by {} <{}>
Report bug: <{}>'''.format(project, version, author, email, github))
        sys.exit()

    elif opts['file'] == 1 and opts['err'] == 0:
        if sys.argv[1].startswith("--file="):
            if os.path.exists(sys.argv[1][7:]):
                return sys.argv[1][7:]
            else:
                print("{}: cannot access '{}': No such file or directory"
                .format(project, sys.argv[1][7:]))
        elif sys.argv[1] in ['--file', '-f']:
            if len(sys.argv) == 2:
                print("Please enter csv file path.")
            elif os.path.exists(sys.argv[2]):
                return sys.argv[2]
            else:
                print("{}: cannot access '{}': No such file or directory"
                .format(project, sys.argv[2]))
        sys.exit()

    elif opts['mode'] == 1 and opts['err'] == 0:
        pass

    elif opts['err'] == 1:
        print('''{_name}: invalid option -- '{}'
Try '{_name} --help' for more information.'''.format(sys.argv[1:], _name=project.lower()))
        sys.exit()

    if len(sys.argv) < 2:
        return "checker_data.csv"

    for argv in sys.argv[1:]:
        if argv.startswith("-") or argv.startswith("--"):
            if argv in ['-h', '--help'] and opts['help'] == 0:
                opts['help'] += 1
            elif argv in ['-v', '--version'] and opts['vers'] == 0:
                opts['vers'] += 1
            elif (argv in ['-f', '--file'] or argv.startswith("--file=")) and opts['file'] == 0:
                opts['file'] += 1
            elif (argv in ['-m', '--mode'] or argv.startswith("--mode=")) and opts['mode'] == 0:
                opts['file'] += 1
            else:
                opts['err'] = 1
    return helper(**opts)


# Main
if __name__ == "__main__":
    csv_path = helper(**{'help': 0, 'vers': 0, 'file': 0, 'mode': 0, 'err': 0})
    data = load_data(csv_path)
    output(title=1)

    try:
        itemlist = list(filter(get_info, data))
    except KeyboardInterrupt:
        pass

    print("Bye~ %s  Working: %s Sec" % localtime(0))
