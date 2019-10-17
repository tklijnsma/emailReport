#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

from time import strftime
datestr = strftime( '%b%d %H:%M:%S' )


########################################
# Main
########################################

def main():

    sendEmail(
        'Test from PSI ({0})'.format(datestr),
        'Test body from PSI ({0})'.format(datestr),
        test=False
        )


def sendEmail(
    subject,
    body,
    test=False,
    ):

    # Make it monospaced
    body = '<font face="Courier New, Courier, monospace"><pre>' + body + '</pre></font>'
    body = body.replace( '\n', '<br>' )



    for emailReceiver in [
        'tklijnsm@gmail.com',
        'derek.feichtinger@psi.ch',
        'vstampf@student.ethz.ch'
        ]:

        # Create a text/plain message
        msg = MIMEText( body, 'html' )

        msg['Subject'] = subject
        msg['From']    = 'tklijnsm.helper@gmail.com'
        # msg['To']      = 'tklijnsm@gmail.com'
        msg['To']      = emailReceiver


        if not test:

            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(
                'tklijnsm.helper@gmail.com',
                'the password'
                )
            server.sendmail( msg['From'], msg['To'], msg.as_string() )
            server.quit()

        else:
            print 'TEST MODE: Sending the following email:'
            print msg






########################################
# End of Main
########################################
if __name__ == "__main__":
    main()