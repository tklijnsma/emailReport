#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os, re, commands, pexpect
from os.path import *
from time import sleep

from userio import decryptString

import ROOT

from time import strftime
datestr = strftime( '%b%d %H:%M:%S' )


########################################
# Main
########################################

TESTMODE = False

def main():

    subjectline, fullreport = testSEOperationsReport()

    print 'SUBJ:'
    print subjectline
    print 'FULL REPORT:'
    print fullreport



report = ''
def testSEOperationsReport():
    global report

    ########################################
    # Environment specifics
    ########################################

    report += '\n' + '- '*30
    report += '\nSome specifics for testing\n'

    report += '\nTime: {0}'.format( datestr )

    cmd_whichroot = "which root"
    status_whichroot, output_whichroot = executeCommand( cmd_whichroot )
    report += '\n' + output_whichroot

    cmd_whichpython = "which python"
    status_whichpython, output_whichpython = executeCommand( cmd_whichpython )
    report += '\n' + output_whichpython


    ########################################
    # Grid certificate
    ########################################

    report += '\n\n' + '- '*30
    report += '\nChecking grid certificate status\n'

    cmd_proxyinfo = 'voms-proxy-info'
    status_proxyinfo, output_proxyinfo = executeCommand( cmd_proxyinfo )

    if status_proxyinfo == 0:
        
        match = re.search( r'timeleft\s*:\s*(\d+):(\d\d):(\d\d)', output_proxyinfo )
        if not match:
            report += '\nERROR: can not extract time left from command output'
        else:
            timeleft = 3600 * int(match.group(1)) + 60 * int(match.group(2)) + int(match.group(3))
            report += '\nTime left: {0}'.format( timeleft )

            if timeleft < 60:
                report += '\nInitiating new proxy for 1 hour'
                cmd_renewproxy = 'voms-proxy-init -voms cms -valid 1:00'
                child = pexpect.spawn( cmd_renewproxy )
                i = child.expect( [pexpect.TIMEOUT, "Enter GRID pass phrase for this identity:"] )
                if i == 0:
                    report += "\nGot unexpected output: %s %s" % (child.before, child.after)

                    report += '\nTrying different expect string'
                    i = child.expect( [pexpect.TIMEOUT, "Enter GRID pass phrase:"] )
                    if i == 0:
                        report += "\nGot unexpected output again: %s %s" % (child.before, child.after)
                        return '', report
                else:
                    # child.sendline( decryptString( 'ex4jVf9cA' ) )
                    child.sendline( decryptString( 'Rx4jVf9cA' ) )

                output_renewproxy = child.read()
                report += '\n' + output_renewproxy

    sleep(1)


    ########################################
    # Perform file operations
    ########################################

    report += '\n\n' + '- '*30
    report += '\nPerforming test file operations\n'

    pnfsTestdir = '/pnfs/psi.ch/cms/trivcat/store/user/tklijnsm/SEtests'

    sampleFile = abspath( join( dirname(__file__), 'smallElectronSample.root' ) )
    sampleFileSE = join( pnfsTestdir, basename(sampleFile) )


    cmd_lsSEdir = "uberftp t3se01.psi.ch 'ls {0}'".format( dirname(pnfsTestdir) )
    status_lsSEdir, output_lsSEdir = executeCommand( cmd_lsSEdir )
    report += '\n' + output_lsSEdir

    try:

        cmd_createSEdir = "uberftp t3se01.psi.ch 'mkdir {0}'".format( pnfsTestdir )
        status_createSEdir, output_createSEdir = executeCommand( cmd_createSEdir )
        report += '\n' + output_createSEdir
        assert status_createSEdir == 0

        cmd_lsSEdir = "uberftp t3se01.psi.ch 'ls {0}'".format( dirname(pnfsTestdir) )
        status_lsSEdir, output_lsSEdir = executeCommand( cmd_lsSEdir )
        report += '\n' + output_lsSEdir
        assert status_lsSEdir == 0

        cmd_copyToSE = "xrdcp {0} {1}".format( sampleFile, 'root://t3dcachedb.psi.ch:1094//' + sampleFileSE )
        status_copyToSE, output_copyToSE = executeCommand( cmd_copyToSE )
        report += '\n' + output_copyToSE
        assert status_copyToSE == 0

        cmd_lsSEdir = "uberftp t3se01.psi.ch 'ls {0}'".format( pnfsTestdir )
        status_lsSEdir, output_lsSEdir = executeCommand( cmd_lsSEdir )
        report += '\n' + output_lsSEdir
        assert status_lsSEdir == 0


        cmd_opendcap = (
            "python -c '" +
            "import ROOT;" +
            "\nrootFp = ROOT.TFile.Open(\"dcap://t3se01.psi.ch:22125/{0}\");" +
            "\ntree = rootFp.Get(\"tree\");" +
            "\ntree.Scan( \"eventNumber:scRawEnergy:genEnergy\", \"\", \"\", 5 );" +
            "\nrootFp.Close();" +
            "'"
            ).format( sampleFileSE )
        status_opendcap, output_opendcap = executeCommand( cmd_opendcap )
        report += '\n' + output_opendcap
        assert status_opendcap == 0


        cmd_openxrootd = (
            "python -c '" +
            "import ROOT;" +
            "\nrootFp = ROOT.TFile.Open(\"root://t3dcachedb.psi.ch:1094/{0}\");" +
            "\ntree = rootFp.Get(\"tree\");" +
            "\ntree.Scan( \"eventNumber:scRawEnergy:genEnergy\", \"\", \"\", 5 );" +
            "\nrootFp.Close();" +
            "'"
            ).format( sampleFileSE )
        status_openxrootd, output_openxrootd = executeCommand( cmd_openxrootd )
        report += '\n' + output_openxrootd
        assert status_openxrootd == 0


    except AssertionError:
        report += '\nThe chain "create directory > copy in file > ls > delete file" was broken'

    finally:
        cmd_removedir = "uberftp t3se01.psi.ch 'rm -r {0}'".format( pnfsTestdir )
        status_removedir, output_removedir = executeCommand( cmd_removedir )
        report += '\n' + output_removedir

    return '', report


def executeCommand( cmd ):
    global report
    report += '\n'
    if TESTMODE:
        report += '\nTESTMODE: ' + cmd
        return 0, '<< no output, cmd not executed in test mode >>'
    else:
        report += '\nEXECUTING: ' + cmd
        # os.system( cmd )
        status, output = commands.getstatusoutput( cmd )
        if not status == 0:
            report += '\nERROR: command has exit status {0}'.format( status )
        return status, output



########################################
# End of Main
########################################
if __name__ == "__main__":
    main()
