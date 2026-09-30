CREATE TABLE `answers` (
	`event_id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`question_id` text NOT NULL,
	`version` integer NOT NULL,
	`submission_id` text NOT NULL,
	`choice_id` text NOT NULL,
	`label` text NOT NULL,
	`question` text NOT NULL,
	`created` text NOT NULL,
	`acknowledged` text
);
--> statement-breakpoint
CREATE UNIQUE INDEX `answer_once` ON `answers` (`owner`,`question_id`,`version`);--> statement-breakpoint
CREATE UNIQUE INDEX `submission_once` ON `answers` (`owner`,`submission_id`);--> statement-breakpoint
CREATE TABLE `deliveries` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`event_id` text NOT NULL,
	`subscription_id` text NOT NULL,
	`status` text NOT NULL,
	`attempts` integer NOT NULL,
	`next_attempt` text NOT NULL,
	`accepted` text,
	`last_error` text,
	`lease_until` text
);
--> statement-breakpoint
CREATE TABLE `questions` (
	`owner` text PRIMARY KEY NOT NULL,
	`id` text NOT NULL,
	`version` integer NOT NULL,
	`question` text NOT NULL,
	`choices` text NOT NULL,
	`expires` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `subscriptions` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`url` text NOT NULL,
	`secret` text NOT NULL,
	`old_secret` text,
	`rotate_until` text,
	`question_id` text,
	`expires` text NOT NULL
);
