#!/bin/bash
echo "Called at $(date)" >> /mnt/t3nfs01/data01/shome/tklijnsm/Scripts/emailReport/runlog.txt
source /mnt/t3nfs01/data01/shome/tklijnsm/Scripts/emailReport/setenv.sh >> /mnt/t3nfs01/data01/shome/tklijnsm/Scripts/emailReport/runlog.txt 2>&1
cd /mnt/t3nfs01/data01/shome/tklijnsm/Scripts/emailReport
python /mnt/t3nfs01/data01/shome/tklijnsm/Scripts/emailReport/makeReportAndSend.py >> /mnt/t3nfs01/data01/shome/tklijnsm/Scripts/emailReport/runlog.txt 2>&1