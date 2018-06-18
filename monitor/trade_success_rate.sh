#!/bin/bash
date=$(date +%Y-%m-%d --date '1 day ago')
python /root/monitor/trade_success_rate.py $date
