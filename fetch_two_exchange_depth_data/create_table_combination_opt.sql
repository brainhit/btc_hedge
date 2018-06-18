CREATE TABLE `combination_opt` (
  `exchange_pair` VARCHAR(100) DEFAULT NULL COMMENT 'exchange pair',
  `symbol` VARCHAR(20) DEFAULT NULL COMMENT 'symbol',
  `opt_num` INT DEFAULT 0 COMMENT 'opportunity num',
  `opt_pos_num` INT DEFAULT 0,
  `opt_neg_num` INT DEFAULT 0,
  `log_date` VARCHAR(50) DEFAULT NULL COMMENT 'log date'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
