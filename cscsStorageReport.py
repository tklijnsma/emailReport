#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os, subprocess, re, sys, argparse


########################################
# Main
########################################

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument( '--check', action='store_true', help='boolean')
    args = parser.parse_args()

    if not args.check:
        subjectline, fullreport = cscsStorageReport( test=True )
        print 'SUBJ:'
        print subjectline
        print 'FULL REPORT:'
        print fullreport

    else:

        # This code used for checking out storage at deeper level

        # ======================================
        # Get relevant part of site readiness html
        
        # overviewHtml = 'http://ganglia.lcg.cscs.ch/ganglia/files_cms.html'
        overviewHtml = 'https://lhcpublic.cscs.ch/files_cms.html'

        html = subprocess.check_output( 'curl -s ' + overviewHtml , shell=True )

        reportCreationTime = re.search( r'Timestamp\:\s(.*?)\s\<br\>', html ).group(1)

        lines = getEntriesInSpecificPath( html, '/store/group/b-physics', nStop=50 )
        for line in lines:
            print printLine( line )



basePath = '/pnfs/lcg.cscs.ch/cms/trivcat/store'
def cscsStorageReport( test=False ):

    VERBOSE = True

    # ======================================
    # Get relevant part of site readiness html
    
    # overviewHtml = 'http://ganglia.lcg.cscs.ch/ganglia/files_cms.html'
    overviewHtml = 'https://lhcpublic.cscs.ch/files_cms.html'

    html = subprocess.check_output( 'curl -s ' + overviewHtml , shell=True )

    # reportCreationTime = re.search( r'Timestamp\:\s(.*?)\s\<br\>', html ).group(1)
    reportCreationTime = re.search(
        r'Generated on storage02.lcg.cscs.ch at (.*?)\<br\>',
        html
        ).group(1)

    # ======================================
    # Get specific numbers

    report = []

    lines = getEntriesAtLevel( html, 0 )

    if len(lines) == 0:
        print 'ERROR: No Lines found'

    for line in lines:

        if VERBOSE:
            print line

        if line['path'].startswith('/pnfs/lcg.cscs.ch/cms/local/arizzi'): continue
        report.append( printLine( line ) )
        if line['path'] == basePath:
            basePathStorage = line['sizeHuman']

    lines = getEntriesAtLevel( html, 1 )
    for line in lines:
        if line['path'].startswith('/pnfs/lcg.cscs.ch/cms/local/arizzi/'): continue
        report.append( printLine( line ) )
        if not test and line['sizeMB'] > 1024**2:
            sublines = getEntriesInSpecificPath( html, line['path'], nStop=15 )
            for subline in sublines:
                report.append( printLine( subline ) )

    report = '\n'.join(report)
    report += '\n'
    report += '\n(/store = {0})'.format(basePath)
    report += '\nReport made on: {0}'.format( reportCreationTime )
    report += '\nFor more information, see:'
    report += '\n' + overviewHtml

    # Find base path size for subject line
    subjectline = 'CSCS Storage: {0}'.format( basePathStorage )

    return subjectline, report


def getEntriesAtLevel( text, level=0 ):

    # --> THERE IS A DEPTH VARIABLE IN THE TABLE!
    # pat = r'.*{0}'.format(basePath)
    # if level > 0:
    #     pat += r'/{0}'.format( '/'.join(['[\s\w\d\-\_\+]*' for i in xrange(level)]) )
    # pat += r'\n'

    pat = r'\s*\d+\s\|\s*{0}\s.*'.format(level+4)

    matches = re.findall( pat, text )

    lines = []
    for match in matches:
        line = interpretLine(match)
        if not line:
            continue
        lines.append(line)
    lines.sort( key=lambda line: line['sizeMB'], reverse=True )

    return lines
        


def getEntriesInSpecificPath( text, path, nStop=None ):
    if path.endswith('/'): path = path[:-1]
    pat = r'.*{0}/[\w\d\-\_\+]*\n'.format(path)

    matches = re.findall( pat, text )

    lines = []
    for match in matches:
        line = interpretLine(match)
        if not line:
            continue
        lines.append(line)
    lines.sort( key=lambda line: line['sizeMB'], reverse=True )

    if nStop and len(lines)>nStop:
        return lines[:nStop]
    else:
        return lines

    # for iLine, line in enumerate(lines):
    #     printLine( line )
    #     if nStop and iLine == nStop-1:
    #         break


    

def humanReadableFileSize( num, suffix='B' ):
    num = float(num)
    for unit in [ '', 'K', 'M', 'G' ]:
        if abs(num) < 1024.0:
            return "{0:.1f} {1}{2}".format( num, unit, suffix )
        num /= 1024.0
    return "{0:.1f} {1}{2}".format( num, 'T', suffix )


def interpretLine( line ):
    components = [ i.strip() for i in line.split('|') if not i.strip()=='' ]
    
    if not len(components) == 6:
        print 'ERROR: unexpected elements in line:'
        print line
        sys.exit()
        return None

    ret = {
        'sizeMB'    : float(components[0]),
        'sizeHuman' : humanReadableFileSize(1024*1024*float(components[0])),
        'depth'     : int(components[1]),
        'ictime'    : components[2],
        'iatime'    : components[3],
        'imtime'    : components[4],
        'path'      : components[5],
        }
    return ret


def printLine( line ):
    return '{0}{1:10s}: {2}'.format( (line['depth']-4)*'    ', line['sizeHuman'], line['path'].replace(basePath,'/store') )


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()