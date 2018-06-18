CREATE TABLE `combination_trade_amount` (
  `combination` VARCHAR(100) DEFAULT NULL COMMENT 'combination name',
  `trade_amount` FLOAT DEFAULT 0.0 COMMENT 'trade amount (big coin based)',
  `hour` VARCHAR(20) DEFAULT NULL COMMENT 'time (hour)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
