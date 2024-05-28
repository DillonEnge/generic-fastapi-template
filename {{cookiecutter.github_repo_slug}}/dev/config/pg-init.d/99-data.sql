--
-- Populate tables with dummy data for local development.
--

-- 00.) Dummy data for the 'operations' table
insert into operations(table_name, create_op, read_op, update_op, delete_op) values
('relationships', true, true, true, true),
('users', true, true, true, true);

-- 01.) Dummy data for the 'relationships' table
-- insert into relationships(primary_table_name, secondary_table_name, primary_table_alias, associative_table_name) values
-- ('users', 'membership', 'user_id', null),
