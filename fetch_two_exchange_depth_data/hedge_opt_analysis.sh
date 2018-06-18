#!/bin/bash
date=$(date +%Y-%m-%d --date '1 day ago')
python /root/fetch_two_exchange_depth_data/hedge_opt_analysis.py $date
