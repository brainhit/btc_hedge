#!/bin/bash
now=`date +%Y-%m-%d`' 00:00'
yes=$(date +%Y-%m-%d --date '1 day ago')' 00:00'
sql="
insert into btc_trade.combination_profit (combination, init_big, init_small, init_bnb, init_huobi, yes_big, yes_small, yes_bnb, yes_huobi, now_big, now_small, now_bnb, now_huobi, daily_profit_rate, total_profit_rate, daily_profit, total_profit, no_fee_daily_profit_rate, no_fee_total_profit_rate, no_fee_daily_profit, no_fee_total_profit, log_time)
select
	a.combination,
	c.big_coin_total,
	c.small_coin_total,
	c.bnb,
	c.huobi_point,
	a.big_coin_total,
	a.small_coin_total,
	a.bnb,
	a.huobi_point,
	b.big_coin_total,
	b.small_coin_total,
	b.bnb,
	b.huobi_point,
	((b.big_coin_total-a.big_coin_total)+(b.small_coin_total-a.small_coin_total)*b.symbol_price+(b.bnb-a.bnb)*b.bnb_price/b.big_coin_btc_price+(b.huobi_point-a.huobi_point)*0.22/b.btc_price/b.big_coin_btc_price)/(a.big_coin_total+a.small_coin_total*a.symbol_price),
	((b.big_coin_total-c.big_coin_total)+(b.small_coin_total-c.small_coin_total)*b.symbol_price+(b.bnb-c.bnb)*b.bnb_price/b.big_coin_btc_price+(b.huobi_point-c.huobi_point)*0.22/b.btc_price/b.big_coin_btc_price)/(c.big_coin_total+c.small_coin_total*c.symbol_price),
        (b.big_coin_total-a.big_coin_total)+(b.small_coin_total-a.small_coin_total)*b.symbol_price+(b.bnb-a.bnb)*b.bnb_price/b.big_coin_btc_price+(b.huobi_point-a.huobi_point)*0.22/b.btc_price/b.big_coin_btc_price,
        (b.big_coin_total-c.big_coin_total)+(b.small_coin_total-c.small_coin_total)*b.symbol_price+(b.bnb-c.bnb)*b.bnb_price/b.big_coin_btc_price+(b.huobi_point-c.huobi_point)*0.22/b.btc_price/b.big_coin_btc_price,
	((b.big_coin_total-a.big_coin_total)+(b.small_coin_total-a.small_coin_total)*b.symbol_price)/(a.big_coin_total+a.small_coin_total*a.symbol_price),
	((b.big_coin_total-c.big_coin_total)+(b.small_coin_total-c.small_coin_total)*b.symbol_price)/(c.big_coin_total+c.small_coin_total*c.symbol_price),
        (b.big_coin_total-a.big_coin_total)+(b.small_coin_total-a.small_coin_total)*b.symbol_price,
        (b.big_coin_total-c.big_coin_total)+(b.small_coin_total-c.small_coin_total)*b.symbol_price,
	'"$now':00'"'
from (
	select *
	from btc_trade.coin_info
	where substring(log_time, 1, 16)='"$yes"'
) a join (
	select * 
	from btc_trade.coin_info
	where substring(log_time, 1, 16)='"$now"'
) b on a.combination=b.combination join (
	select *
	from btc_trade.coin_info
	where status='Start'
) c on a.combination=c.combination;
"

mysql -h rm-6weqcc0l0228vku03.mysql.japan.rds.aliyuncs.com -u taohuashan -p123@admin -e "${sql}"

cd /root/coin-project-0.3.0
python coin/tasklet/email_report.py profit >> /var/logs/email_profit_report.log 2>&1 &
