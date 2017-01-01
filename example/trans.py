#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: mosquito
@email: sensor.wen@gmail.com
@project: autotrans
@github: http://github.com/1dot75cm/repo-checker
@description: Auto translate po file.
@version: 0.1
@history:
    0.1 - Initial version (2016.02.26)
'''

from __future__ import print_function, unicode_literals
import os
import sys
import re
import polib
import requests
import argparse

def get_translate(text):
    url = 'http://translate.google.cn/'
    data = dict(hl='en', sl='en', tl='zh-CN', text=text)
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, params=data, headers=headers)
    if resp.ok:
        return re.search("TRANSLATED_TEXT='(.*?)';", resp.text).group(1)
    return ""

def replace_words(text, word_dict):
    ''' https://segmentfault.com/q/1010000002474308 '''
    yo = re.compile('|'.join(map(re.escape, word_dict)))
    def translate(match):
        return word_dict[match.group(0)]
    return yo.sub(translate, text)

def invert_dict(d):
    return dict([(v,k) for k,v in d.items()])

def helper():
    ''' display help information.'''

    parser = argparse.ArgumentParser(description='Auto translate po file.')
    parser.add_argument('-f', '--file', metavar='PATH', required='True',
                        dest='files', action='store',
                        help='po file path'
                       )
    args = parser.parse_args()

    if args.files and os.path.exists(args.files):
        opts['input_file'] = args.files
    elif args.files is not None:
        print("AutoTrans: cannot access '{}': No such file or directory"
            .format(args.files))
        sys.exit()

def open_pofile():
    po = polib.pofile(opts['input_file'])
    for i in po.untranslated_entries():
        print('Translating line {}:'.format(i.linenum), i.msgid)
        text = replace_words(i.msgid, s)
        i.msgstr = replace_words(get_translate(text), r)
        i.flags = ['fuzzy']
    po.save(opts['input_file'] + '.translated')

if __name__ == '__main__':
    global s, r, opts
    s = {
         '<':'_lt_',
         '>':'_gt_',
         '{':'_ls_',
         '}':'_gs_',
         '(':'_lk_',
         ')':'_gk_',
         "'":'_dot_',
         '"':'_dd_',
         '&':'_amp_',
         '$':'_amb_',
         '%':'_amc_',
         '=':'_eq_',
         '/':'_es_',
         '\n':'_cs_'
        }
    r = invert_dict(s)
    opts = {'input_file': 'test.po'}

    helper()
    open_pofile()
