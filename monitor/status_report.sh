#!/bin/bash
cd /root/coin-project-0.3.0
python coin/tasklet/email_report.py status >> /var/logs/email_status_report.log 2>&1 &
