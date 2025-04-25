CREATE TABLE IF NOT EXISTS `event_users` (
  `user_id`  INT(11) NOT NULL COMMENT 'FK → users.user_id',
  `event_id` INT(11) NOT NULL COMMENT 'FK → events.event_id',
  PRIMARY KEY (`user_id`,`event_id`),
  FOREIGN KEY (`user_id`)  REFERENCES `users`(`user_id`)  ON DELETE CASCADE,
  FOREIGN KEY (`event_id`) REFERENCES `events`(`event_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="Invitee list per event";
