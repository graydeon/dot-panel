CREATE TABLE `status_updates` (
	`owner` text PRIMARY KEY NOT NULL,
	`summary` text NOT NULL,
	`projects` text NOT NULL,
	`source_timestamp` text NOT NULL,
	`updated_at` text NOT NULL
);
