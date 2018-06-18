CREATE TABLE `combination_trade_success_rate` (
  `combination` VARCHAR(100) DEFAULT NULL COMMENT 'combination name',
  `trade_success_rate` FLOAT DEFAULT 0.0 COMMENT 'trade success rate',
  `trade_num` INT DEFAULT 0 COMMENT 'trade number',
  `dt` VARCHAR(20) DEFAULT NULL COMMENT 'dt'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
