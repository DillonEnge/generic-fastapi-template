create table if not exists operations (
  id uuid primary key default uuid_generate_v4(),
  table_name varchar not null,
  create_op boolean default false,
  read_op boolean default true,
  update_op boolean default false,
  delete_op boolean default false,
  constraint unique_operations_table_name unique (table_name)
);
