#!/usr/bin/env python2
#coding=utf-8
'''
@author: mosquito
@email: sensor.wen@gmail.com
@project: Checker
@github: http://github.com/1dot75cm/repo-checker
@description: Checker is used to check update for software.
@version: 0.2
@history:
    0.2 - Add help info, use multithread (2016.01.10)
    0.1 - Initial version (2016.01.05)
'''

from __future__ import print_function
from threading  import Thread
from Queue      import Queue
import urllib
import re
import time
import csv
import json
import sys
import os
import argparse

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
    except (AttributeError, TypeError):
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
    except (AttributeError, TypeError):
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

def helper():
    ''' display help information.
    return csv_path, thread_num'''

    thread_num = 10
    data_file = 'checker_data.csv'
    doclist = list()

    for i in __doc__.splitlines():
        if i.startswith("@") and i.find(": ") > -1:
            doclist.append(i.split(': ')[1])
    _author, _email, _project, _github, _description, _version = doclist

    parser = argparse.ArgumentParser(description=_description)

    parser.add_argument('-n', '--number', metavar='NUM', type=int,
                        dest='numbers', action='store',
                        help='{_name} work number of thread(default: 10)'.format(
                            _name=_project.lower())
                       )

    parser.add_argument('-f', '--file', metavar='PATH',
                        dest='files', action='store',
                        help='{_name} data(csv) full path'.format(
                            _name=_project.lower())
                       )

    parser.add_argument('-v', '--version', dest='version', action='store_true',
                        help='output version information and exit')

    args = parser.parse_args()

    if args.version:
        print('{} version {}\nWritten by {} <{}>\nReport bug: <{}>'.format(
                 _project, _version, _author, _email, _github)
             )
        sys.exit()

    if args.files and os.path.exists(args.files):
        data_file = args.files
    elif args.files is not None:
        print("{}: cannot access '{}': No such file or directory"
            .format(_project, args.files))
        sys.exit()

    if args.numbers:
        thread_num = args.numbers

    return data_file, thread_num

def working(q):
    ''' get content from queue. '''

    while True:
        value = [q.get(),]
        list(filter(get_info, value))
        q.task_done()

def running(Num=10, *data):
    ''' Mutilthreads test: 1, 569s; 5, 107s; 10, 54s; 15, 37s
    create threads, and put data to queue. '''

    q = Queue()

    for i in range(Num):
        t = Thread(target=working, args=(q,))
        t.setDaemon(True)
        t.start()

    for value in data:
        q.put(value)

    q.join()


if __name__ == "__main__":
    csv_path, thread_num = helper()
    data = load_data(csv_path)
    output(title=1)

    try:
        running(thread_num, *data)
    except KeyboardInterrupt:
        pass

    print("Bye~ %s  Working: %s Sec" % localtime(0))
