CREATE TABLE `owner_layouts` (
	`owner` text PRIMARY KEY NOT NULL,
	`version` integer NOT NULL,
	`layouts` text NOT NULL,
	`previous_layouts` text,
	`updated_at` text NOT NULL
);
