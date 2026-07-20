ALTER TABLE mailbox_accounts
ADD CONSTRAINT ck_mailbox_account_auth_mode
CHECK (auth_mode IN ('desktop_oauth', 'web_oauth'));
