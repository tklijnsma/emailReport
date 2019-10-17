#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os, sys
import argparse
import commands

from os.path import *


########################################
# Main
########################################

def main():
    checkPermission()

    parser = argparse.ArgumentParser()
    parser.add_argument( 'password', type=str, default='default', help='default string' )
    args = parser.parse_args()

    encryptedPassword = encryptString( args.password )
    print 'Encrypted password:', encryptedPassword

    decryptedPassword = decryptString( encryptedPassword )
    print 'Decrypted password:', decryptedPassword


def encryptString( password ):
    checkPermission()
    keyStr = getKey( len(password) )
    shifter, backshifter = letterShifter()
    res = ''
    for pwChar, keyChar in zip(password[:], keyStr[:]):
        pwOrd = ord(pwChar)
        keyOrd = ord(keyChar)
        res += shifter( pwOrd, keyOrd )
    return res


def decryptString( password ):
    checkPermission()
    keyStr = getKey( len(password) )
    shifter, backshifter = letterShifter()
    res = ''
    for pwChar, keyChar in zip(password[:], keyStr[:]):
        pwOrd = ord(pwChar)
        keyOrd = ord(keyChar)
        res += backshifter( pwOrd, keyOrd )
    return res


def letterShifter():
    checkPermission()

    upperRange = range( ord('A'), ord('Z')+1 )
    lowerRange = range( ord('a'), ord('z')+1 )
    numberRange = range( ord('0'), ord('9')+1 )
    alfabet = upperRange + lowerRange + numberRange
    alfabet.append( ord('.') )
    nAlfabet = len(alfabet)

    def shifter( pw, key ):
        pw = int(pw)
        key = int(key)
        if not pw in alfabet or not key in alfabet:
            return pw
        iOut = alfabet.index(pw) + alfabet.index(key) + 1
        while iOut >= nAlfabet:
            iOut -= nAlfabet
        return chr( alfabet[iOut] )

    def backshifter( spw, key ):
        spw = int(spw)
        key = int(key)
        if not spw in alfabet or not key in alfabet:
            return spw
        iOut = alfabet.index(spw) - alfabet.index(key) - 1
        while iOut < 0:
            iOut += nAlfabet
        return chr( alfabet[iOut] )

    return shifter, backshifter


def getKey( n ):
    checkPermission()
    keyFile = expanduser( '~/.ssh/id_rsa' )
    with open( keyFile, 'r' ) as keyFp:
        lines = keyFp.readlines()
    keyStr = lines[1][:n]
    return keyStr


def checkPermission():
    status, output = commands.getstatusoutput( 'whoami' )
    if not output == 'tklijnsm':
        print 'User {0} is not permitted to execute this function'.format( output )
        sys.exit()


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()