# -*- coding=utf-8 -*-
# author: ouyan
# date: 2018-03-10
# comment: util

def symbol_transform(symbol, exchange):
        if exchange == 'huobi':
                return symbol.replace('/', '')
        elif exchange == 'binance':
                return symbol.replace('/', '').upper()
	elif exchange == 'okex':
		return symbol.replace('/', '_')
	elif exchange == 'hitbtc':
		return symbol.replace('/', '').upper()
	elif exchange == 'bittrex':
		tmp = symbol.split('/')
		res = tmp[1].upper() + '-' + tmp[0].upper()
		return res
        else:
                return ''

def find_profit(bids_info, asks_info):
    """
    寻找获利空间
    :param bids_info: [[price, amount], [price_amoun] ... ] 按照买价从高到低排序
    :param asks_info: [[price, amount], [price_amoun] ... ] 按照卖价从低到高排序
    :return: bid_price, ask_price, amount
    """
    index_bid, index_ask = 0, 0
    bid_price, ask_price, amount = 0.0, 0.0, 0.0
    while index_bid < len(bids_info) and index_ask < len(asks_info):
        # 可获利，看看能成交数量多少
        if (bids_info[index_bid][0] - asks_info[index_ask][0]) / (asks_info[index_ask][0] + bids_info[index_bid][0]) * 2 > 0.003:
            bid_price = bids_info[index_bid][0]
            ask_price = asks_info[index_ask][0]
            if asks_info[index_ask][1] > bids_info[index_bid][1]:
                amount += bids_info[index_bid][1]
                asks_info[index_ask][1] -= bids_info[index_bid][1]
                bids_info[index_bid][1] = 0.0
                index_bid += 1
            else:
                amount += asks_info[index_ask][1]
                bids_info[index_bid][1] -= asks_info[index_ask][1]
                asks_info[index_ask][1] = 0.0
                index_ask += 1
        else:
            break
    return bid_price, ask_price, amount
