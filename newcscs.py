#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os, subprocess, re, sys, argparse
from datetime import datetime


########################################
# Main
########################################

def main():
    overview_url = 'https://lhcpublic.cscs.ch/files_cms.html'
    generator = CSCSGenerator()
    tree = generator.get_from_url(overview_url)
    print tree.email_report(minsize=1024.)


def newcscs_report(test=None):
    overview_url = 'https://lhcpublic.cscs.ch/files_cms.html'
    generator = CSCSGenerator()
    tree = generator.get_from_url(overview_url)
    
    report = 'Report made on {0}, using {1}\n{2}'.format(
        tree.ts,
        overview_url,
        tree.email_report()
        )
    return '', report


class Tree(object):
    """docstring for Tree"""
    def __init__(self, inodes, ts=None):
        super(Tree, self).__init__()
        self.inodes = inodes
        if ts is None:
            self.ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S (retrieval time)')
        else:
            self.ts = ts

    def email_report(self, minsize=1024.**3):
        # Filter
        inodes = []
        for inode in self.inodes:
            if (
                    (inode.relpath.startswith('store/user') or inode.relpath.startswith('store/group'))
                    and inode.reldepth <= 2
                    and inode.size > minsize
                    ):
                inodes.append(inode)
            elif inode.reldepth <= 1:
                inodes.append(inode)

        inodes = sort_inodes(inodes)
        return '\n'.join([ str(n) for n in inodes ])


def sort_inodes(inodes):
    print 'Sorting inodes'
    depths = [ n.reldepth for n in inodes ]
    min_depth = min(depths)
    max_depth = max(depths)

    roots = [ n for n in inodes if n.reldepth == min_depth ]
    roots.sort(key=lambda n: -n.size)

    sorted_inodes = []
    for root in roots:
        for node in traverse(root, inodes):
            sorted_inodes.append(node)
    return sorted_inodes


def traverse(root, inodes):
    yield root
    children = [ n for n in inodes if n.reldepth == root.reldepth+1 and n.relpath.startswith(root.relpath) ]
    children.sort(key=lambda n: -n.size)
    for child in children:
        for c in traverse(child, inodes):
            yield c



class Inode(object):

    basepath = '/pnfs/lcg.cscs.ch/cms/trivcat'

    """docstring for Inode"""
    def __init__(self):
        super(Inode, self).__init__()
        self.path = None
        self.date  = None
        self.size = None

    def from_line(self, line):
        components = line.split()
        self.size = int(components[0])
        self.size_hr = size_humanreadable(self.size*1024.)
        self.path = components[3]
        self.date = datetime.strptime(
            components[1] + ' ' + components[2],
            '%Y-%m-%d %H:%M'
            )
        self.depth = self.get_depth(self.path)
        self.get_rel_path(self.path)
        return self

    def get_depth(self, path):
        return path.count('/')

    def get_rel_path(self, path):
        self.relpath = os.path.relpath(path, self.basepath)
        self.reldepth = self.relpath.count('/')

    def tabstring(self):
        return '    '*self.reldepth + '{0:10}: {1}'.format(self.size_hr, self.relpath)

    def __repr__(self):
        return self.tabstring()


class CSCSGenerator(object):
    """docstring for CSCSGenerator"""
    def __init__(self):
        super(CSCSGenerator, self).__init__()
        self.raw = ''
        
    def get_from_url(self, url):
        raw = subprocess.check_output('curl -s ' + url , shell=True)
        ts = self.get_timestamp(raw)
        print 'Timestamp:', ts
        inodes = self.get_inodes(self.get_lines(raw))
        return Tree(inodes, ts)


    def get_timestamp(self, text):
        """Try to get timestamp from raw text; if failing, just use a local timestamp"""
        match = re.search(
            r'Generated on storage02.lcg.cscs.ch at (.*?)\<br\>',
            text
            )
        if match:
            ts = match.group(1)
        else:
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S (retrieval time)')
        return ts


    def get_lines(self, text):
        print 'Getting lines...'
        # Lines should be in between a single <pre> tag pair
        text = text.split('<pre>')[1]
        text = text.split('</pre>')[0]
        lines = [ l.strip() for l in text.split('\n') if not len(l.strip())==0 ]
        return lines


    def get_inodes(self, lines):
        print 'Lines to inodes...'
        return [ Inode().from_line(l) for l in lines ]


def size_humanreadable(num, suffix='B'):
    num = float(num)
    for unit in [ '', 'K', 'M', 'G' ]:
        if abs(num) < 1024.0:
            return "{0:.1f} {1}{2}".format( num, unit, suffix )
        num /= 1024.0
    return "{0:.1f} {1}{2}".format( num, 'T', suffix )

#____________________________________________________________________
if __name__ == "__main__":
    main()
