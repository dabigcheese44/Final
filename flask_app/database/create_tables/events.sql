CREATE TABLE IF NOT EXISTS `events` (
  `event_id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `title`    VARCHAR(100) NOT NULL COMMENT 'Event title',
  `created_by` INT(11) NOT NULL COMMENT 'FK → users.user_id',
  `start_date` DATE NOT NULL COMMENT 'First day (inclusive)',
  `end_date`   DATE NOT NULL COMMENT 'Last day (inclusive)',
  `day_start_time` TIME NOT NULL COMMENT 'Earliest time collected each day',
  `day_end_time`   TIME NOT NULL COMMENT 'Latest time collected each day',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created timestamp',
  PRIMARY KEY (`event_id`),
  FOREIGN KEY (`created_by`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="Scheduling events";
