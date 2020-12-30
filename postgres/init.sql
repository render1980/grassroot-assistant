create user grassroot with password 'grassroot';
create schema if not exists grassroot authorization grassroot;

create table if not exists grassroot.groups (
    id serial PRIMARY KEY,
    group_name varchar(256),
    description text,
    admin_id bigint,
    longitude double precision,
    latitude double precision,
    token varchar(256),
    creation_date timestamp NOT NULL
);

grant all privileges on all tables in schema grassroot to grassroot;
