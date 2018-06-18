#!/bin/bash
status=$(supervisorctl status)
now=$(date +"%Y-%m-%d %H:%M:%S")
ip=$(/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')
sql="INSERT INTO btc_trade.supervisor_status (host, log_time, info) VALUES('${ip}', '${now}', '${status}')"
mysql -h rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com -u taohuashan -p123@admin -e "${sql}"
