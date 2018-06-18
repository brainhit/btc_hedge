CREATE TABLE `two_exchange_hedge_depth` (
  `log_date` varchar(30) DEFAULT NULL COMMENT 'log date',
  `symbol` varchar(20) DEFAULT NULL COMMENT 'trade symbol',
  `exchange_pair` varchar(50) DEFAULT NULL COMMENT 'exchange pair; example: binance/huobi; binance: exchange1; huobi: exchange2',
  `exchange1_bids` varchar(1024) DEFAULT NULL COMMENT 'exchange 1 bids data',
  `exchange1_asks` varchar(1024) DEFAULT NULL COMMENT 'exchange 1 asks data',
  `exchange2_bids` varchar(1024) DEFAULT NULL COMMENT 'exchange 2 bids data',
  `exchange2_asks` varchar(1024) DEFAULT NULL COMMENT 'exchange 2 asks data'
);
