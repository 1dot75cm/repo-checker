#!/bin/python3
import os
import sys
import bs4
import urllib, urllib.error
import subprocess

def get(url):
    try:
        return urllib.request.urlopen(url).read()
    except Exception as e:
        print(e)
        return ''

def link(page, attrs=None):
    urls = []
    soup = bs4.BeautifulSoup(page, "lxml")
    divs = soup.findAll("div", attrs=attrs)
    for div in divs:
        a = div.find('a')
        if a:
            urls.append(site + a['href'])
    return urls

def link2(page, attrs=None):
    soup = bs4.BeautifulSoup(page, "lxml")
    a = soup.find('a', attrs=attrs)
    return a['href']

if __name__ == "__main__":
    site = "http://folio.co.in/"
    page = "?page="
    #uri = site + "categories/" + sys.argv[1] + "/" + page
    categories = link(get(site+"categories/"), {"class":"col s6 m4 l4"})

    for i in categories:
        pdfs = []
        uri = i + page
        category = i.split('/')[-2]
        if not os.path.exists(category):
            print('# mkdir %s' % category)
            os.mkdir(category)
        else:
            print('skip %s' % category)
            continue
        print('# cd %s' % category)
        os.chdir(category)

        for p in range(1, 50):
            print('page', uri+str(p))
            urls = link(get(uri+str(p)), {"class":"hide-on-small-only"})
            for index,url in enumerate(urls):
                print('Parser url%s: %s' % (index, url))
                pdfs.append(link2(get(url), {"onclick":"downloadBook()"}))
            if len(urls) < 10:
                break

        for index,pdf in enumerate(pdfs):
            print('Downloading file%s: %s' % (index, pdf))
            #urllib.request.urlretrieve(pdf, filename=)
            subprocess.getoutput('/bin/axel -n4 %s' % pdf)

        os.chdir('..')
