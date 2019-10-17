#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os, subprocess, re, sys
from os.path import *

from time import strftime
datestr = strftime( '%b%d %H:%M:%S' )


########################################
# Main
########################################

def main():

    subjectline, fullreport = t3StorageReport( test=True )

    print 'SUBJ:'
    print subjectline
    print 'FULL REPORT:'
    print fullreport


basePath = '/pnfs/psi.ch/cms/trivcat/store'
def t3StorageReport( test=False ):

    overviewHtml = 'http://t3mon.psi.ch/ganglia/PSIT3-custom/v_pnfs_top_dirs.txt'
    lines = getLines( overviewHtml )

    report = []

    cutoffsize = 0.1*1024*1024  # 100 Gb
    report.append( printLine(atLevel( lines, 0 )[0]) )
    for line in atLevel( lines, 1 ):
        if line['sizeMB'] > cutoffsize:
            report.append( printLine(line) )
            for subline in atLevel( lines, 2, line['shortpath'] ):
                if subline['sizeMB'] > cutoffsize:
                    report.append( printLine(subline) )


    report = '\n'.join(report)
    report += '\n'
    report += '\n(store = {0})'.format(basePath)
    report += '\nReport made on: {0}'.format( datestr )
    report += '\nFor more information, see:'
    report += '\n' + overviewHtml

    # Find base path size for subject line
    subjectline = ''

    return subjectline, report



def atLevel( lines, level, startswith='' ):
    return [ line for line in lines if line['level'] == level and line['shortpath'].startswith(startswith) ]


def getLines( overviewHtml = 'http://t3mon.psi.ch/ganglia/PSIT3-custom/v_pnfs_top_dirs.txt' ):

    # ======================================
    # Get relevant part of site readiness html
    
    txt = subprocess.check_output( 'curl -s ' + overviewHtml , shell=True )


    # ======================================
    # Get specific numbers

    lines = []
    for iLine, line in enumerate(txt.split('\n')):
        if iLine < 2: continue

        line = interpretLine( line, basePath )
        if line == None:
            continue

        if line['depth'] >= 4 and line['depth'] <=7:
            lines.append(line)

    return lines



def humanReadableFileSize( num, suffix='B' ):
    num = float(num)
    for unit in [ '', 'K', 'M', 'G' ]:
        if abs(num) < 1024.0:
            return "{0:.1f} {1}{2}".format( num, unit, suffix )
        num /= 1024.0
    return "{0:.1f} {1}{2}".format( num, 'T', suffix )

def interpretLine( line, basePath ):
    components = [ i.strip() for i in line.split('|') if not i.strip()=='' ]

    if not len(components) == 7:
        # print 'ERROR: unexpected elements in line:'
        # print line
        return None

    ret = {
        'sizeMB'    : float(components[0]),
        'sizeHuman' : humanReadableFileSize(1024*1024*float(components[0])),
        'depth'     : int(components[1]),
        'level'     : int(components[1])-4,
        'iuid'      : components[2],
        'igid'      : components[3],
        'ictime'    : components[4],
        'iatime'    : components[5],
        'path'      : components[6],
        'shortpath' : components[6].replace( basePath, basename(basePath) ),
        }

    return ret

def printLine( line ):
    return '{0}{1:10s}: {2}'.format( (line['level'])*'    ', line['sizeHuman'], line['shortpath'] )




########################################
# End of Main
########################################
if __name__ == "__main__":
    main()