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
        else:
                return ''
