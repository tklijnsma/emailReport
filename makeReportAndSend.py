#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os, sys

from sendEmail import sendEmail

from siteReadinessReport import siteReadinessReport
from t3StorageReport import t3StorageReport
from testSEOperationsReport import testSEOperationsReport

# # from cscsStorageReport import cscsStorageReport
# sys.path.append('../T2tools/')
# sys.path.append('../T2tools/PrintStorageOverview/')
# from T2StorageOverview import dailyReport_T2Storage

import newcscs


from time import strftime
datestr = strftime( '%b%d %H:%M:%S' )

# TESTMODE = True
TESTMODE = False

########################################
# Main
########################################

def main():

    subject = ''
    report = ''

    subject, report = appendReport( subject, report, 'Site Readiness report', siteReadinessReport )
    subject, report = appendReport( subject, report, 'CSCS storage report', newcscs.newcscs_report )
    subject, report = appendReport( subject, report, 'T3 Storage report', t3StorageReport )
    subject, report = appendReport( subject, report, 'Storage element file operations report', testSEOperationsReport )

    subject = 'Report | ' + subject
    subject += ' ({0})'.format(datestr)

    if TESTMODE:
        print '\nPrint of subject:\n'
        print subject
        print '\nPrint of report:\n'
        print report
        print '\nSubmitting test email:\n'
        sendEmail(
            subject,
            report,
            test=True
            )

    else:
        sendEmail(
            subject,
            report,
            )


def appendReport( fullSubject, fullReport, reportName, reportFunction ):

    fullReport += '\n\n' + '-'*67
    fullReport += '\n{0}\n'.format( reportName )

    try:
        subject, report = reportFunction()
        if subject != '' and fullSubject != '': fullSubject += ', '
        fullSubject += subject
        fullReport += report + '\n'

    except:
        fullReport += 'ERROR when running {0}()\n'.format( reportFunction.__name__ )

    return fullSubject, fullReport


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()