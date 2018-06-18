CREATE TABLE `combination_payment` (
  `combination` VARCHAR(100) DEFAULT NULL COMMENT 'combination name',
  `total_profit` FLOAT DEFAULT 0.0 COMMENT 'total_profit (big coin based)',
  `payment_status` INT DEFAULT 0 COMMENT 'payment status'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
