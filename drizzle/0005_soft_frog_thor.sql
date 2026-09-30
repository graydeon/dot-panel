CREATE TABLE `question_queue` (
	`owner` text NOT NULL,
	`id` text NOT NULL,
	`version` integer NOT NULL,
	`question` text NOT NULL,
	`choices` text NOT NULL,
	`expires` text NOT NULL,
	`created` text NOT NULL,
	`status` text NOT NULL,
	PRIMARY KEY(`owner`, `id`)
);
--> statement-breakpoint
CREATE TABLE `queue_imports` (
	`owner` text PRIMARY KEY NOT NULL,
	`imported_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `usage_snapshots` (
	`owner` text PRIMARY KEY NOT NULL,
	`source` text NOT NULL,
	`fetched_at` text NOT NULL,
	`saved_at` text NOT NULL,
	`payload` text NOT NULL
);
