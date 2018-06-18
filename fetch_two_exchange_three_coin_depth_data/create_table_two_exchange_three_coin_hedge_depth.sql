CREATE TABLE `two_exchange_three_coin_hedge_depth` (
  `log_date` varchar(30) DEFAULT NULL COMMENT 'log date',
  `symbol` varchar(20) DEFAULT NULL COMMENT 'trade symbol',
  `exchange_pair` varchar(50) DEFAULT NULL COMMENT 'exchange pair; example: binance/huobi; binance: exchange1; huobi: exchange2',
  `exchange1_symbol1_bids` varchar(1024) DEFAULT NULL COMMENT 'exchange 1 symbol 1 bids data',
  `exchange1_symbol1_asks` varchar(1024) DEFAULT NULL COMMENT 'exchange 1 symbol 1 asks data',
  `exchange1_symbol2_bids` varchar(1024) DEFAULT NULL COMMENT 'exchange 1 symbol 2 bids data',
  `exchange1_symbol2_asks` varchar(1024) DEFAULT NULL COMMENT 'exchange 1 symbol 2 asks data',
  `exchange2_symbol1_bids` varchar(1024) DEFAULT NULL COMMENT 'exchange 2 symbol 1 bids data',
  `exchange2_symbol1_asks` varchar(1024) DEFAULT NULL COMMENT 'exchange 2 symbol 1 asks data',
  `exchange2_symbol2_bids` varchar(1024) DEFAULT NULL COMMENT 'exchange 2 symbol 2 bids data',
  `exchange2_symbol2_asks` varchar(1024) DEFAULT NULL COMMENT 'exchange 2 symbol 2 asks data'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
