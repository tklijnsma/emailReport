#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os, subprocess, re

from time import strftime
datestr = strftime( '%b%d %H:%M:%S' )

from datetime import date
thisMonth = date.today().month
thisDay   = date.today().day

monthDict = {
    1  : 'Jan',
    2  : 'Feb',
    3  : 'Mar',
    4  : 'Apr',
    5  : 'May',
    6  : 'Jun',
    7  : 'Jul',
    8  : 'Aug',
    9  : 'Sep',
    10 : 'Oct',
    11 : 'Nov',
    12 : 'Dec',
    }

########################################
# Main
########################################

def main():

    subjectline, fullreport = siteReadinessReport()

    print 'SUBJ:'
    print subjectline
    print 'FULL REPORT:'
    print fullreport


def siteReadinessReport():

    # ======================================
    # Get relevant part of site readiness html
    
    startAnchor = r'<a name="T2_CH_CSCS"></a>'
    endAnchor   = r'<a name="T2_CH_CSCS_HPC"></a>'
    SiteReadinessHtml = 'https://cms-site-readiness.web.cern.ch/cms-site-readiness/SiteReadiness/HTML/SiteReadinessReport.html#T2_CH_CSCS'
    # Does not work on python 2.6...
    fullHtml = subprocess.check_output( 'curl -s ' + SiteReadinessHtml , shell=True )
    iStartAnchor = fullHtml.index(startAnchor)
    iEndAnchor = fullHtml.index(endAnchor)
    html = fullHtml[iStartAnchor:iEndAnchor]


    # ======================================
    # Get specific numbers

    # Metrics header
    # <tr><td width="325"><div id="metrics-header">SAM Availability: </div></td>

    # Metric
    # <td width="45" bgcolor=green>
    # <a href="http://wlcg-sam-cms.cern.ch/templates/ember/#/historicalsmry/heatMap?end_time=2017%2F02%2F27%2023%3A00&granularity=Default&group=AllGroups&profile=CMS_CRITICAL_FULL&site=T2_CH_CSCS&site_metrics=undefined&start_time=2017%2F02%2F27%2000%3A00&time=Enter%20Date...&type=Availability%20Ranking%20Plot&view=Site%20Availability">
    # <div id="metrics2">100%
    # </div>
    # </a>
    # </td>

    # pat = r'<div id="metrics-header">SAM Availa.*?</tr>'
    # match = re.search( pat, html, re.DOTALL )

    # if match:
    #     print 'FOUND MATCH:'
    #     print match.group(0)
    # else:
    #     print 'no match'

    # return 0


    metrics = [
        'LifeStatus',
        'Site Readiness',
        'Maintenance',
        'HammerCloud',
        'SAM Availability',
        'Good T2 links from T1s',
        'Good T2 links to T1s',
        'Active T2 links from T1s',
        'Active T2 links to T1s',
        ]

    metricDict = {}
    for metric in metrics:

        pat = r'<div id="metrics-header">{0}.*?</tr>'.format(metric)
        rowMatch = re.search( pat, html, re.DOTALL )

        if not rowMatch:
            print 'No match for metric "{0}"; continuing'.format( metric )
            continue

        row = rowMatch.group(0)

        # print row
        metricPat = r'<div id=".*?">(.*?)</div>'
        metricValues = re.findall( metricPat, row, re.DOTALL )

        if metricValues[0].startswith(metric): metricValues.pop(0)

        metricDict[metric] = metricValues



    # ======================================
    # Get dates

    datePat = r'<div id="date">(.*?)</div>'
    dates = re.findall( datePat, html )



    # ======================================
    # Dict per date entry

    stats = []

    for iEntry in xrange(len(metricDict['Site Readiness'])):
        stat = {}

        for metric in metrics:
            stat[metric] = metricDict[metric][iEntry]

        # Bit hacky with the date: if iDay > thisDay, it was probably from last month
        iDay = int(dates[iEntry])
        if iDay > thisDay:
            month = thisMonth-1
            if month == 0: month = 12
        else:
            month = thisMonth

        stat['date'] = '{0}{1:02d}'.format( monthDict[month], iDay )

        stats.append(stat)


    # ======================================
    # Format something pretty

    lines = []

    # Return formatted string for only the last N
    useLastN = 8
    useStats = stats[-useLastN:]

    colw = max( map( len, metrics ) )
    p = lambda text, length: '{{0:>{0}s}}'.format(length).format(text)

    dateline = p( 'Date', colw ) + ': ' + '|'.join( [ p( s['date'], 5 ) for s in useStats ] )
    lines.append( dateline )

    for metric in metrics:
        line  = ''
        line += p( metric, colw ) + ': '
        line += '|'.join( [ p( s[metric].replace('&check;','V'), 5 ) for s in useStats ] )
        lines.append(line)

    fullreport = 'Full report of the last {0} days:\n'.format( useLastN )
    fullreport += '\n'.join(lines)
    fullreport += '\n\nFor more details, see:'
    fullreport += '\n' + SiteReadinessHtml

    # ======================================
    # Find last filled in report

    for stat in reversed(useStats):
        if not stat['Site Readiness'].strip() == '':
            mostRecentStat = stat
            break

    subjectline = 'Report '
    subjectline += mostRecentStat['date'] + ': '

    shortstats = []
    shortstats.append( 'LS={0}'.format( mostRecentStat['LifeStatus'].replace('&check;','V') ) )
    shortstats.append( 'SR={0}'.format( mostRecentStat['Site Readiness'] ) )
    shortstats.append( 'SAM={0}'.format( mostRecentStat['SAM Availability'] ) )
    shortstats.append( 'HC={0}'.format( mostRecentStat['HammerCloud'] ) )
    subjectline += ', '.join(shortstats)
    subjectline += ' ({0})'.format(datestr)

    return subjectline, fullreport



########################################
# End of Main
########################################
if __name__ == "__main__":
    main()