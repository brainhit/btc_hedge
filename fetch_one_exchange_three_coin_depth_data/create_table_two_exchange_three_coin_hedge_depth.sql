CREATE TABLE `one_exchange_three_coin_depth` (
  `log_time` VARCHAR(30) DEFAULT NULL COMMENT 'log tim',
  `symbol` VARCHAR(30) DEFAULT NULL COMMENT 'trade symbol',
  `exchange` VARCHAR(20) DEFAULT NULL COMMENT 'exchange name',
  `symbol1_bids` VARCHAR(1024) DEFAULT NULL COMMENT 'symbol1 bids data',
  `symbol1_asks` VARCHAR(1024) DEFAULT NULL COMMENT 'symbol1 asks data',
  `symbol2_bids` VARCHAR(1024) DEFAULT NULL COMMENT 'symbol2 bids data',
  `symbol2_asks` VARCHAR(1024) DEFAULT NULL COMMENT 'symbol2 asks data',
  `symbol3_bids` VARCHAR(1024) DEFAULT NULL COMMENT 'symbol3 bids data',
  `symbol3_asks` VARCHAR(1024) DEFAULT NULL COMMENT 'symbol3 asks data'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
