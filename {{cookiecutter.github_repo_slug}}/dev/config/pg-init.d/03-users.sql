CREATE TABLE IF NOT EXISTS users
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    first_name character varying COLLATE pg_catalog."default" NOT NULL,
    middle_name character varying COLLATE pg_catalog."default",
    last_name character varying COLLATE pg_catalog."default" NOT NULL,
    email character varying COLLATE pg_catalog."default" NOT NULL,
    primary_phone character varying COLLATE pg_catalog."default" NOT NULL,
    description character varying COLLATE pg_catalog."default",
    timezone character varying COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT clock_timestamp(),
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);
