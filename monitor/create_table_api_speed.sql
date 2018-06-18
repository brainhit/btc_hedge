CREATE TABLE `api_speed` (
  `exchange` VARCHAR(20) DEFAULT NULL COMMENT 'exchange',
  `forward_time` VARCHAR(20) DEFAULT NULL COMMENT 'forward api time',
  `backward_time` VARCHAR(20) DEFAULT NULL COMMENT 'backward api time',
  `total_time` VARCHAR(20) DEFAULT NULL COMMENT 'total api time',
  `log_time` VARCHAR(50) DEFAULT NULL COMMENT 'log_time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
