import { sqliteTable, text, integer, uniqueIndex } from 'drizzle-orm/sqlite-core';
export const questions = sqliteTable('questions', {
 owner:text('owner').primaryKey(), id:text('id').notNull(), version:integer('version').notNull(), question:text('question').notNull(), choices:text('choices').notNull(), expires:text('expires').notNull()
});
export const answers = sqliteTable('answers', {
 eventId:text('event_id').primaryKey(), owner:text('owner').notNull(), questionId:text('question_id').notNull(), version:integer('version').notNull(), submissionId:text('submission_id').notNull(), choiceId:text('choice_id').notNull(), label:text('label').notNull(), question:text('question').notNull(), created:text('created').notNull(), acknowledged:text('acknowledged')
},t=>[uniqueIndex('answer_once').on(t.owner,t.questionId,t.version),uniqueIndex('submission_once').on(t.owner,t.submissionId)]);
export const subscriptions=sqliteTable('subscriptions',{
 id:text('id').primaryKey(), owner:text('owner').notNull(), url:text('url').notNull(), secret:text('secret').notNull(), oldSecret:text('old_secret'), rotateUntil:text('rotate_until'), questionId:text('question_id'), expires:text('expires').notNull()
});
export const deliveries=sqliteTable('deliveries',{
 id:text('id').primaryKey(), owner:text('owner').notNull(), eventId:text('event_id').notNull(), subscriptionId:text('subscription_id').notNull(), status:text('status').notNull(), attempts:integer('attempts').notNull(), nextAttempt:text('next_attempt').notNull(), accepted:text('accepted'), lastError:text('last_error'), leaseUntil:text('lease_until')
});
export const statusUpdates=sqliteTable('status_updates',{
 owner:text('owner').primaryKey(), summary:text('summary').notNull(), projects:text('projects').notNull(), sourceTimestamp:text('source_timestamp').notNull(), updatedAt:text('updated_at').notNull()
});
export const ownerSettings=sqliteTable('owner_settings',{
 owner:text('owner').primaryKey(), dotDisplayName:text('dot_display_name').notNull(), updatedAt:text('updated_at').notNull()
});
