CREATE TABLE IF NOT EXISTS `availabilities` (
  `availability_id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `event_id`   INT(11) NOT NULL COMMENT 'FK → events.event_id',
  `user_id`    INT(11) NOT NULL COMMENT 'FK → users.user_id',
  `slot_start` DATETIME NOT NULL COMMENT 'Start of 30‑min slot (aligned)',
  `avail_status` ENUM('available','maybe','unavailable') NOT NULL DEFAULT 'unavailable',
  UNIQUE KEY `uniq_slot` (`event_id`,`user_id`,`slot_start`),
  PRIMARY KEY (`availability_id`),
  FOREIGN KEY (`event_id`) REFERENCES `events`(`event_id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`)  REFERENCES `users`(`user_id`)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="Per‑user availability per slot";
