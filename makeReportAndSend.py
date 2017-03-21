#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import os

from sendEmail import sendEmail
from siteReadinessReport import siteReadinessReport


########################################
# Main
########################################

def main():

    subject, report = siteReadinessReport()

    sendEmail(
        subject,
        report,
        # test=True
        )


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()