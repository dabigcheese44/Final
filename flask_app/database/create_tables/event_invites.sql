CREATE TABLE IF NOT EXISTS event_invites (
  invite_id   INT AUTO_INCREMENT PRIMARY KEY,
  event_id    INT NOT NULL,
  email       VARCHAR(100) NOT NULL,
  user_id     INT NULL,
  invited_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)  REFERENCES users(user_id)  ON DELETE SET NULL,
  UNIQUE KEY event_email (event_id, email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
