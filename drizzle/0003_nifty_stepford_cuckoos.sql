CREATE TABLE `calendar_snapshots` (
	`owner` text PRIMARY KEY NOT NULL,
	`calendar_name` text NOT NULL,
	`timezone` text NOT NULL,
	`range_start` text NOT NULL,
	`range_end` text NOT NULL,
	`source_synced_at` text NOT NULL,
	`saved_at` text NOT NULL,
	`events` text NOT NULL
);
