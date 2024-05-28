create table if not exists relationships (
  id uuid primary key default uuid_generate_v4(),
  primary_table_name varchar not null,
  secondary_table_name varchar not null,
  primary_table_alias varchar default null,
  associative_table_name varchar default null
);
