#!/bin/bash
hour=$(date '+%Y-%m-%d %H' --date '9 hours ago')
python /root/monitor/trade_amount.py $hour
