#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: mosquito
@email: sensor.wen@gmail.com
@project: Checker
@github: http://github.com/1dot75cm/repo-checker
@description: Checker is used to check update for software.
@version: 0.4
@history:
    0.4 - Add user-agent, gzip, http-proxy, aio support(2016.01.28)
    0.3 - Use class (2016.01.24)
    0.2 - Add help info, use multithread (2016.01.10)
    0.1 - Initial version (2016.01.05)
'''

from threading  import Thread
from queue      import Queue
import urllib.request, urllib.parse, urllib.error
import re, csv, json
import time, sys, os
import argparse, random
import gzip, ssl
from io import BytesIO
import asyncio, aiohttp
import tqdm, signal

class GzipHandler(urllib.request.BaseHandler):
    ''' A handler to add gzip capabilities to urllib requests '''

    def http_request(self, req):
        req.add_header('Accept-Encoding', 'gzip')
        return req

    def http_response(self, req, resp):
        old_resp = resp    # resp.headers
        data = resp.read()  # 内存中的数据，只能读一次
        try:
            content = gzip.GzipFile(fileobj = BytesIO(data), mode = 'r').read()
        except OSError:
            content = data
        fp = BytesIO(content)  # File-like-obj具有read()方法
        resp = urllib.request.addinfourl(fp, old_resp.headers, old_resp.url, old_resp.code)
        resp.msg = old_resp.msg
        return resp

    https_request = http_request
    https_response = http_response

class Checker(object):
    ''' check update for software '''

    def __init__(self, *args):
        self.sub_pkg, self.url_type, self.name, self.url = args[:4]
        self.branch,  self.rpm_com,  self.rpm_date       = args[4:7]
        self.release_date = self.release_com = ""
        self.latest_date  = self.latest_com  = ""
        self.status = ""

        self.ualist = [
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; rv:41.0) Gecko/20100101 Firefox/41.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/40.0',
            'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0;  rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'
        ]

    def get_page(self, _url):
        ''' 获取整个页面数据
        return str '''

        header = { 'Accept-Encoding': 'gzip' }
        header['User-Agent'] = self.ualist[random.randint(0, len(self.ualist)-1)]
        if opts['user_agent']: header['User-Agent'] = opts['user_agent']

        req  = urllib.request.Request(url = _url, headers = header)
        pros = opts['proxy']
        if pros and pros[0] in ('http', 'https'):
            req.set_proxy(pros[1], pros[0])
        # urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
        # https://www.python.org/dev/peps/pep-0476/
        context = ssl._create_unverified_context()
        page = urllib.request.urlopen(req, timeout=80, context=context).read()

        #gzip_handler = GzipHandler()
        #proxy_handler = urllib.request.ProxyHandler({'https':'XX.XX.XX.XX:XXXX'})
        #proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()
        #proxy_auth_handler.add_password('realm', 'host', 'username', 'password')
        #opener = urllib.request.build_opener(gzip_handler, proxy_handler, proxy_auth_handler)
        #opener.addheaders = [('User-Agent', 'Python-urllib/2.7')]
        #urllib.request.install_opener(opener)
        #page = opener.open(_url).read()

        try:
            if self.url_type == "2": return "None Content"
            if self.url_type == "4": return gzip.decompress(page).decode('gb2312').encode('utf-8')
            else:                    return gzip.decompress(page)
        except OSError:
            return page

    def get_date(self, _page):
        ''' 获取 date -> 150708
        return short_time(str) '''

        time_format = "%Y-%m-%d"
        pattern = b'.*datetime="(.*?)T'

        if self.url_type in ["4", "6", "14"]:
            pattern = b'([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})'
        elif self.url_type == "5":
            _page = _page.split(b"tragtor")[4]
            pattern = b'time.>(.*[0-9]{4})'
            time_format = "%a %b %d %H:%M:%S %Y"
        elif self.url_type == "7":
            if _page.splitlines()[-3].find(b"info") > -1:
                _page = _page.splitlines()[-4]
            else:
                _page = _page.splitlines()[-3]
            pattern = b'([0-9]{2}-.{3}-[0-9]{4})'
            time_format = "%d-%b-%Y"
        elif self.url_type == "8":
            pattern = b'tag.*([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})'
        elif self.url_type == "9":
            pattern = b'id=\w{40}.*([0-9]{4}-[0-9]{2}-[0-9]{2})'
        elif self.url_type == "10":
            pattern = b'([0-9]{2}\s.{3}\s[0-9]{4})'
            time_format = "%d %b %Y"
        elif self.url_type == "11":
            pattern = b'([A-Z].*\s[0-9]{1,2},\s[0-9]{4})'
            time_format = "%B %d, %Y"
        elif self.url_type == "12":
            pattern = b'id=\w{40}.*tag-deco.*([0-9]{4}-[0-9]{2}-[0-9]{2})'
        elif self.url_type == "20":
            pattern = b'([0-9]{2}-.{3}-[0-9]{4})'
            time_format = "%d-%b-%Y"
        elif self.url_type == "21":
            _page = json.loads(_page.decode())['PCC'][0]['date'].encode()
            pattern = b'(.*)'
        elif self.url_type == "22":
            _page = re.findall(b'.*364.*', _page)[-1]
            pattern = b'([0-9]{2}-\w{3}-[0-9]{4})'
            time_format = "%d-%b-%Y"

        try:
            d = re.search(pattern, _page, re.M).group(1).decode()
            t = time.strptime(d, time_format)
            return time.strftime("%y%m%d", t)
        except (AttributeError, TypeError):
            return "None"

    def get_commit(self, _page):
        ''' 获取 commit
        return commit(str) '''

        pattern = b'.*commit/([a-z0-9]*)\"'

        if self.url_type == "9":
            pattern = b'id=(\w{40})'
        elif self.url_type == "12":
            pattern = b'id=(\w{40}).*tag-deco'

        try:
            return re.search(pattern, _page, re.M).group(1).decode()
        except (AttributeError, TypeError):
            return "None"

    def get_info(self):
        ''' 获取页面commit和date
        return datalist'''

        type_num = ["3", "4", "5", "6", "7", "9", "10", "11", "12", "14", "20", "21", "22"]

        if self.url_type in type_num:
            release_url = self.url.replace('%2',',')
            p1 = self.get_page(release_url)
            self.release_date, self.release_com = self.get_date(p1), self.get_commit(p1)
            self.latest_date, self.latest_com = self.release_date, self.release_com
        elif self.url_type != "2":
            release_url = self.url + "/releases"
            latest_url = self.url + "/commits/" + self.branch

            p1, p2 = self.get_page(release_url), self.get_page(latest_url)
            self.release_date, self.release_com = self.get_date(p1), self.get_commit(p1)
            self.latest_date, self.latest_com = self.get_date(p2), self.get_commit(p2)

        if self.rpm_date == self.latest_date or self.rpm_date >= self.release_date:
            self.status = "normal"
        else:
            self.status = "update" + "[" + self.url + "]"

    def output(self):
        ''' Output.
        Sub Package: 0. normal 1. subpkg '''

        name = "- " + self.name if self.sub_pkg == "1" else self.name
        rpm_ver = self.rpm_date + "[" + self.rpm_com[:7] + "]"
        rel_ver = self.release_date + "[" + self.release_com[:7] + "]"
        lat_ver = self.latest_date + "[" + self.latest_com[:7] + "]"
        print(str(name).ljust(22) + \
              str(rpm_ver).ljust(16) + \
              str(rel_ver).ljust(16) + \
              str(lat_ver).ljust(16) + \
              str(self.status))

class CheckerAIO(Checker):

    @asyncio.coroutine
    def get_page(self, _url):
        ''' 获取整个页面数据
        return str '''

        header = { 'Accept-Encoding': 'gzip' }
        header['User-Agent'] = self.ualist[random.randint(0, len(self.ualist)-1)]
        if opts['user_agent']: header['User-Agent'] = opts['user_agent']

        with (yield from semaphore):
            response = yield from aiohttp.request('GET', _url, headers = header)
            page = yield from response.read()

        try:
            if self.url_type == "2": return "None Content"
            if self.url_type == "4": return gzip.decompress(page).decode('gb2312').encode('utf-8')
            else:                    return gzip.decompress(page)
        except OSError:
            return page

    @asyncio.coroutine
    def get_info(self):
        ''' 获取页面commit和date
        return datalist'''

        type_num = ["3", "4", "5", "6", "7", "9", "10", "11", "12", "14", "20", "21", "22"]

        if self.url_type in type_num:
            release_url = self.url.replace('%2',',')
            p1 = yield from self.get_page(release_url)
            self.release_date, self.release_com = self.get_date(p1), self.get_commit(p1)
            self.latest_date, self.latest_com = self.release_date, self.release_com
        elif self.url_type != "2":
            release_url = self.url + "/releases"
            latest_url = self.url + "/commits/" + self.branch

            p1 = yield from self.get_page(release_url)
            p2 = yield from self.get_page(latest_url)
            self.release_date, self.release_com = self.get_date(p1), self.get_commit(p1)
            self.latest_date, self.latest_com = self.get_date(p2), self.get_commit(p2)

        if self.rpm_date == self.latest_date or self.rpm_date >= self.release_date:
            self.status = "normal"
        else:
            self.status = "update" + "[" + self.url + "]"

class Helper(object):

    def __init__(self):
        global opts
        opts = {
            'thread_num': 10,
            'input_file': 'checker_data.csv',
            'user_agent': None,
            'proxy'     : None,
            'mode'      : 'aio'
        }
        self.helper()
        self.q = Queue()
        self.localtime(1)

    def inputs(self):
        ''' Load csv file.

        CSV Format:
          "1,1,lwqq,https://github.com/xiehuc/lwqq,master,733836e,150202"

        Sub Package: 0. normal 1. subpkg
        Url Type: 1. github 2. google 3. bitbucket 4. sogou 5. tragtor 6. youdao
          7. opera 8. pacman 9. apt 10. nginx 11. ccal 12. sandbox 14. wps
          20. qt-installer-freamwork 21. pycharm
        Name, Url, Branch, RPM Commit, RPM Update Time, Others

        return list '''

        csvlist = []
        with open(opts['input_file'], 'r') as csvfile:
            content = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in content:
                if len(row) != 0 and row[0][0] != "#":
                    csvlist.append(row)
        return csvlist

    def output(self, title=None):
        ''' Output. '''

        if title == 1:
            print("# Generation date:", self.localtime(0)[0], \
                  "\n Name".ljust(23) + \
                  "RPM-Version".ljust(16) + \
                  "Rel-Version".ljust(16) + \
                  "Latest-Commit".ljust(16) + \
                  "Status")
        else:
            print("Bye~ %s  Working: %s Sec" % self.localtime(0))

    def localtime(self, trigger=1):
        ''' return current localtime and seconds. '''

        global start_sec, stop_sec
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if trigger == 1:
            start_sec = time.time()
        elif trigger == 0:
            stop_sec = time.time()
            return (local_time, stop_sec - start_sec)

    def helper(self):
        ''' display help information.
        return csv_path, thread_num'''

        doclist = []
        for i in __doc__.splitlines():
            if i.startswith("@") and i.find(": ") > -1:
                doclist.append(i.split(': ')[1])
        _author, _email, _project, _github, _description, _version = doclist

        parser = argparse.ArgumentParser(description=_description)

        parser.add_argument('-n', '--number', metavar='NUM', type=int,
                            dest='numbers', action='store',
                            help='{_name} work number of thread(default: 10)'.format(
                                _name=_project.lower()))

        parser.add_argument('-f', '--file', metavar='PATH',
                            dest='files', action='store',
                            help='{_name} data file(csv) full path'.format(
                                _name=_project.lower()))

        parser.add_argument('-U', '--user-agent', metavar='AGENT', type=str,
                            dest='user_agent', action='store',
                            help='user identify as AGENT(default: random)')

        parser.add_argument('-x', '--proxy', metavar='PROTOCOL://HOST:PORT', type=str,
                            dest='proxy', action='store',
                            help='use proxy on given port')

        parser.add_argument('-m', '--mode', dest='mode', action='store',
                            choices={'thread','aio'}, default='aio',
                            help='multi-tasking mode(default: aio)')

        parser.add_argument('-v', '--version', dest='version', action='store_true',
                            help='output version information and exit')

        args = parser.parse_args()

        if args.version:
            print('{} version {}\nWritten by {} <{}>\nReport bug: <{}>'.format(
                  _project, _version, _author, _email, _github))
            sys.exit()

        if args.files and os.path.exists(args.files):
            opts['input_file'] = args.files
        elif args.files is not None:
            print("{}: cannot access '{}': No such file or directory"
                .format(_project, args.files))
            sys.exit()

        if args.numbers:
            opts['thread_num'] = args.numbers
        if args.user_agent:
            opts['user_agent'] = args.user_agent
        if args.proxy:
            opts['proxy'] = re.split('://', args.proxy)
        if args.mode:
            opts['mode'] = args.mode

    def working(self):
        ''' get content from queue. '''

        while True:
            obj = self.q.get()
            obj.get_info()
            self.q.task_done()

    def running(self, *args):
        ''' Mutilthreads test: 1, 569s; 5, 107s; 10, 54s; 15, 37s
        create threads, and put data to queue. '''

        for i in range(opts['thread_num']):
            t = Thread(target=self.working, args=())
            t.setDaemon(True)
            t.start()

        for item in args:
            self.q.put(item)
        self.q.join()

    @asyncio.coroutine
    def progress(self, coros):
        for obj in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
            yield from obj

    def interrupt(self):
        for task in asyncio.Task.all_tasks():
            task.cancel()

if __name__ == "__main__":
    tools = Helper()

    objlist = []
    for i in tools.inputs():
        if opts['mode'] == 'aio':
            objlist.append(CheckerAIO(*i))
        else:
            objlist.append(Checker(*i))

    try:
        if opts['mode'] == 'thread':
            tools.running(*objlist)
        else:
            global semaphore
            semaphore = asyncio.Semaphore(opts['thread_num'])
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(signal.SIGINT, tools.interrupt) # 捕捉信号
            tasks = [i.get_info() for i in objlist]
            loop.run_until_complete(tools.progress(tasks))
    except (KeyboardInterrupt, asyncio.CancelledError, urllib.error.URLError):
        pass

    tools.output(1)
    for obj in objlist:
        obj.output()
    tools.output()
