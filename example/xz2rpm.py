#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: mosquito
@email: sensor.wen@gmail.com
@project: xz2rpm
@github: http://github.com/1dot75cm/repo-checker
@description: xz(PKGBUILD) tranlate to rpm(spec).
@version: 0.1
@history:
    0.1 - Initial version (2016.03.15)
'''

import os
import sys
import re
import json
import time
import argparse

class Package:

    def __init__(self):
        self.opts = {
            'input_file': '',
            'author': '',
            'mail': ''
            }
        self.helper()
        self.data = self.openfile(self.opts['input_file'])
        self.pkg = {
            'pkgbase': '',
            'pkgname': '',
            'pkgver': '',
            'pkgrel': '',
            'epoch': '',
            'pkgdesc': '',
            'arch': '',
            'url': '',
            'license': '',
            'groups': '',
            'depends': '',
            'optdepends': '',
            'makedepends': '',
            'checkdepends': '',
            'provides': '',
            'conflicts': '',
            'replaces': '',
            'backup': '',
            'options': '',
            'install': '',
            'changelog': '',
            'source': '',
            'noextract': '',
            'prepare': '',
            'build': '',
            'check': '',
            'package': ''
            }
        self.pkg_dict = {
            '"': '',
            "'": '',
            '$pkgname': self.pkg['pkgname'],
            '$startdir': '%{_topdir}',
            '$srcdir': '%{_builddir}',
            '$pkgdir': '%{buildroot}'
            }

    def openfile(self, filename):
        with open(filename, 'r') as fs:
            content = fs.read()
        return content

    def _tojson(self, data):
        # TODO
        return json.loads(data, 'utf-8')

    def parse(self, item):
        real_item = None
        patterns = ['=\((.*?)\)', '=(.*)', '\(\)\s*\{(.*)\}']
        for i in patterns:
            pattern = item + i
            if i == '=(.*)':
                val = re.compile(pattern)
            else:
                val = re.compile(pattern, re.S)
            if not val.search(self.data):
                continue
            else:
                self.pkg[item] = val.search(self.data).groups()[0]
                real_item = item
                break
        return real_item

    def replace_words(self, text, word_dict):
        ''' https://segmentfault.com/q/1010000002474308 '''
        yo = re.compile('|'.join(map(re.escape, word_dict)))
        def translate(match):
            return word_dict[match.group(0)]
        return yo.sub(translate, text)

    def get_item(self):
        list(map(self.parse, self.pkg))
        for i in self.pkg:
            self.pkg[i] = self.replace_words(self.pkg[i], self.pkg_dict)

    def output(self):
        self.get_item()
        author = self.opts['author']
        email = self.opts['mail']
        date = time.strftime('%a %b %d %Y', time.localtime())
        content = '''%global debug_package %nil

Name:    {name}
Epoch:   {epoch}
Version: {ver}
Release: {rel}%?dist
Summary: {desc}

Group:   {group}
License: {license}
URL:     {url}
Source0: {src}

BuildArch: {arch}
BuildRequires: {makereq}
Requires: {req}
Recommends: {optreq}

Provides: {prov}
Conflicts: {conf}
Obsoletes: {repl}

%description
{desc}

%prep
%setup -q
{prep}

%build
%configure
make %?_smp_mflags
{build}

%install
%make_install
{install}

%check
{check}

%post
/bin/touch --no-create %_datadir/icons/hicolor &>/dev/null ||:
/usr/bin/update-desktop-database -q ||:

%postun
if [ $1 -eq 0 ]; then
     /bin/touch --no-create %_datadir/icons/hicolor &>/dev/null ||:
     /usr/bin/gtk-update-icon-cache -f -t -q %_datadir/icons/hicolor ||:
fi
/usr/bin/update-desktop-database -q ||:

%posttrans
/usr/bin/gtk-update-icon-cache -f -t -q %_datadir/icons/hicolor ||:

%files
%defattr(-,root,root,-)
%doc README
%license LICENSE

%changelog
* {date} {author} <{email}> - {ver}-{rel}
- '''.format(
            name=self.pkg['pkgname'],
            epoch=self.pkg['epoch'],
            ver=self.pkg['pkgver'],
            rel=self.pkg['pkgrel'],
            desc=self.pkg['pkgdesc'],
            group=self.pkg['groups'],
            license=self.pkg['license'],
            url=self.pkg['url'],
            src=self.pkg['source'],
            arch=self.pkg['arch'],
            makereq=self.pkg['makedepends'],
            req=self.pkg['depends'],
            optreq=self.pkg['optdepends'],
            prov=self.pkg['provides'],
            conf=self.pkg['conflicts'],
            repl=self.pkg['replaces'],
            prep=self.pkg['prepare'],
            build=self.pkg['build'],
            install=self.pkg['package'],
            check=self.pkg['check'],
            date=date,
            author=author,
            email=email
           )
        print(content)

    def helper(self):
        ''' display help information.'''

        parser = argparse.ArgumentParser(description='PKGBUILD translate to Spec.')
        parser.add_argument('-f', '--file', metavar='PATH', type=str,
                            dest='files', action='store', default='PKGBUILD',
                            help='PKGBUILD file'
                            )
        parser.add_argument('-a', '--author', metavar='NAME', type=str,
                            dest='author', action='store', default='Li Lei',
                            help='author of package'
                            )
        parser.add_argument('-m', '--mail', metavar='MAIL', type=str,
                            dest='mail', action='store', default='hanmeimei@gmail.com',
                            help='email address of author'
                            )
        args = parser.parse_args()

        if args.files and os.path.exists(args.files):
            self.opts['input_file'] = args.files
        elif args.files is not None:
            print("xz2rpm: cannot access '{}': No such file or directory"
                 .format(args.files))
            sys.exit()

        if args.author:
            self.opts['author'] = args.author

        if args.mail:
            self.opts['mail'] = args.mail

if __name__ == '__main__':
    item = Package()
    item.output()
